#!/bin/sh

set -eu

BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
DAILY_BACKUP_DIR="${DAILY_BACKUP_DIR:-${BACKUP_DIR}/daily}"
WEEKLY_BACKUP_DIR="${WEEKLY_BACKUP_DIR:-${BACKUP_DIR}/weekly}"
DB_HOST="${DB_HOST:-dblocal}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-medsync}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
BACKUP_INTERVAL_SECONDS="${BACKUP_INTERVAL_SECONDS:-86400}"
BACKUP_DAILY_RETENTION_DAYS="${BACKUP_DAILY_RETENTION_DAYS:-14}"
BACKUP_WEEKLY_RETENTION_DAYS="${BACKUP_WEEKLY_RETENTION_DAYS:-35}"
BACKUP_WEEKLY_DAY="${BACKUP_WEEKLY_DAY:-7}"

timestamp() {
  date +"%d/%m/%Y %H:%M:%S"
}

wait_for_database() {
  echo "$(timestamp) | Waiting for database at ${DB_HOST}:${DB_PORT}..."

  until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
    sleep 2
  done

  echo "$(timestamp) | Database is available"
}

ensure_backup_dir() {
  mkdir -p "$DAILY_BACKUP_DIR" "$WEEKLY_BACKUP_DIR"
}

cleanup_old_daily_backups() {
  find "$DAILY_BACKUP_DIR" -type f -name "*.sql.gz" -mtime +"$BACKUP_DAILY_RETENTION_DAYS" -delete
}

cleanup_old_weekly_backups() {
  find "$WEEKLY_BACKUP_DIR" -type f -name "*.sql.gz" -mtime +"$BACKUP_WEEKLY_RETENTION_DAYS" -delete
}

build_backup_filename() {
  backup_type="$1"
  target_dir="$2"
  echo "${target_dir}/medsync_${DB_NAME}_${backup_type}_$(date +"%Y%m%d_%H%M%S").sql.gz"
}

write_backup_file() {
  backup_file="$1"

  echo "$(timestamp) | Starting backup: ${backup_file}"
  PGPASSWORD="$DB_PASSWORD" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --clean \
    --if-exists \
    --no-owner \
    --no-privileges | gzip > "$backup_file"
  echo "$(timestamp) | Backup completed: ${backup_file}"
}

run_daily_backup() {
  ensure_backup_dir

  backup_file="$(build_backup_filename daily "$DAILY_BACKUP_DIR")"
  write_backup_file "$backup_file"
  cleanup_old_daily_backups
}

should_create_weekly_backup() {
  current_weekday="$(date +%u)"
  [ "$current_weekday" = "$BACKUP_WEEKLY_DAY" ]
}

run_weekly_backup() {
  ensure_backup_dir

  backup_file="$(build_backup_filename weekly "$WEEKLY_BACKUP_DIR")"
  write_backup_file "$backup_file"
  cleanup_old_weekly_backups
}

run_scheduled_backups() {
  run_daily_backup

  if should_create_weekly_backup; then
    run_weekly_backup
  fi
}

run_loop() {
  wait_for_database

  while true; do
    run_scheduled_backups
    echo "$(timestamp) | Sleeping for ${BACKUP_INTERVAL_SECONDS} seconds"
    sleep "$BACKUP_INTERVAL_SECONDS"
  done
}

command="${1:-loop}"

case "$command" in
  once)
    wait_for_database
    run_scheduled_backups
    ;;
  daily)
    wait_for_database
    run_daily_backup
    ;;
  weekly)
    wait_for_database
    run_weekly_backup
    ;;
  loop)
    run_loop
    ;;
  *)
    echo "Usage: $0 [once|daily|weekly|loop]"
    exit 1
    ;;
esac
