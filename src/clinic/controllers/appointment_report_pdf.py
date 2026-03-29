from io import BytesIO

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas:
    """Canvas auxiliar que registra as páginas para desenhar a paginação ao final."""

    def __init__(self, *args, **kwargs):
        from reportlab.pdfgen.canvas import Canvas

        self._canvas = Canvas(*args, **kwargs)
        self._saved_page_states = []

    def __getattr__(self, name):
        """Delegação simples para o canvas real do ReportLab."""
        return getattr(self._canvas, name)

    def showPage(self):
        """Armazena o estado da página atual antes de avançar para a próxima."""
        self._saved_page_states.append(dict(self._canvas.__dict__))
        self._canvas._startPage()

    def save(self):
        """Desenha a paginação em todas as páginas antes de salvar o arquivo."""
        total_pages = len(self._saved_page_states)
        self._canvas.setTitle("Relatorio de Consultas")

        for state in self._saved_page_states:
            self._canvas.__dict__.update(state)
            self._draw_page_number(total_pages)
            self._canvas.showPage()

        self._canvas.save()

    def _draw_page_number(self, total_pages):
        """Desenha o rodapé institucional com a página atual e o total de páginas."""
        self._canvas.setFont("Helvetica", 9)
        self._canvas.setFillColor(colors.HexColor("#4b5563"))
        self._canvas.drawString(12 * mm, 8 * mm, "Portal MedSync")
        self._canvas.drawRightString(
            285 * mm,
            8 * mm,
            f"{self._canvas._pageNumber}/{total_pages}",
        )


class AppointmentReportPdfController:
    """Controller responsável por gerar o PDF do relatório de consultas."""

    def generate_pdf(self, report_data):
        """Gera o PDF do relatório e o devolve em memória."""
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            leftMargin=12 * mm,
            rightMargin=12 * mm,
            topMargin=12 * mm,
            bottomMargin=12 * mm,
        )

        story = []
        styles = self._build_styles()

        if report_data["scope"] == "doctor":
            story.extend(
                self._build_doctor_section(
                    header=report_data["header"],
                    columns=report_data["columns"],
                    rows=report_data["rows"],
                    totals=report_data["totals"],
                    styles=styles,
                )
            )
        else:
            story.extend(
                self._build_all_doctors_sections(
                    report_data=report_data,
                    styles=styles,
                )
            )

        document.build(story, canvasmaker=NumberedCanvas)
        buffer.seek(0)
        return buffer

    def _build_all_doctors_sections(self, *, report_data, styles):
        """Monta os blocos do relatório quando o período inclui todos os médicos."""
        story = []

        for index, doctor_data in enumerate(report_data["doctors"]):
            if index:
                story.append(PageBreak())

            story.extend(
                self._build_doctor_section(
                    header=doctor_data["header"],
                    columns=report_data["columns"],
                    rows=doctor_data["rows"],
                    totals=doctor_data["totals"],
                    styles=styles,
                )
            )

        if report_data["doctors"]:
            story.append(PageBreak())

        story.extend(
            self._build_totals_section(
                title="Totais gerais do relatório",
                totals=report_data["totals"],
                styles=styles,
            )
        )

        return story

    def _build_doctor_section(self, *, header, columns, rows, totals, styles):
        """Monta um bloco completo do relatório para um médico."""
        story = self._build_header_section(header=header, styles=styles)
        story.extend(
            [
                Spacer(1, 6 * mm),
                self._build_table(columns=columns, rows=rows, styles=styles),
                Spacer(1, 4 * mm),
            ]
        )
        story.extend(
            self._build_totals_section(
                title="Totais do período",
                totals=totals,
                styles=styles,
            )
        )

        return story

    def _build_header_section(self, *, header, styles):
        """Monta o cabeçalho institucional do relatório, com logo quando disponível."""
        logo = self._build_logo()
        right_block = [
            Paragraph(header["company_name"], styles["company"]),
            Spacer(1, 1.5 * mm),
            Paragraph("Relatório de Consultas", styles["title"]),
            Spacer(1, 3 * mm),
            self._build_header_meta_table(header=header, styles=styles),
        ]

        if logo:
            header_table = Table(
                [[logo, right_block]],
                colWidths=[84 * mm, 196 * mm],
            )
            header_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (0, 0), (0, 0), "LEFT"),
                        ("ALIGN", (1, 0), (1, 0), "CENTER"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            return [header_table]

        return right_block

    @staticmethod
    def _build_logo():
        """Carrega o logo da clínica quando o arquivo existir no caminho configurado."""
        logo_path = getattr(settings, "CLINIC_LOGO_PATH", None)

        if not logo_path:
            return None

        try:
            logo = Image(str(logo_path), width=52 * mm, height=52 * mm)
            logo.hAlign = "LEFT"
            return logo
        except (FileNotFoundError, OSError):
            return None

    def _build_header_meta_table(self, *, header, styles):
        """Monta o quadro de metadados do cabeçalho do relatório."""
        meta_rows = [
            [
                Paragraph("<b>Médico:</b>", styles["meta_label"]),
                Paragraph(header["doctor_name"], styles["meta_value"]),
            ],
            [
                Paragraph("<b>CRM:</b>", styles["meta_label"]),
                Paragraph(header.get("doctor_crm") or "-", styles["meta_value"]),
            ],
            [
                Paragraph("<b>Período:</b>", styles["meta_label"]),
                Paragraph(
                    f"{header['start_date']} até {header['end_date']}",
                    styles["meta_value"],
                ),
            ],
        ]

        table = Table(meta_rows, colWidths=[28 * mm, 120 * mm], hAlign="RIGHT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f4f6")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        return table

    def _build_table(self, *, columns, rows, styles):
        """Monta a tabela principal do relatório."""
        table_data = [columns]

        for row in rows:
            table_data.append(
                [
                    Paragraph(str(row["Nº"]), styles["table_cell_center"]),
                    Paragraph(str(row["Código"]), styles["table_cell_center"]),
                    Paragraph(row["Paciente"], styles["table_cell"]),
                    Paragraph(row["Tipo"], styles["table_cell"]),
                    Paragraph(row["Pagamento"], styles["table_cell"]),
                    Paragraph(row["Valor Total"], styles["table_cell_right"]),
                    Paragraph(row["Valor Médico"], styles["table_cell_right"]),
                    Paragraph(row["Valor Clínica"], styles["table_cell_right"]),
                    Paragraph(row["Observação"] or "-", styles["table_cell"]),
                ]
            )

        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[
                12 * mm,
                30 * mm,
                50 * mm,
                28 * mm,
                32 * mm,
                24 * mm,
                24 * mm,
                24 * mm,
                49 * mm,
            ],
            hAlign="CENTER",
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("LEADING", (0, 0), (-1, -1), 10),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (1, -1), "CENTER"),
                    ("ALIGN", (5, 0), (7, -1), "RIGHT"),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

    def _build_totals_section(self, *, title, totals, styles):
        """Monta a seção de totais do relatório."""
        totals_table_data = [[Paragraph(title, styles["totals_title"]), ""]]

        for payment_total in totals["by_payment_method"]:
            totals_table_data.append(
                [
                    Paragraph(payment_total["label"], styles["totals_label"]),
                    Paragraph(f"R$ {payment_total['value']}", styles["totals_amount"]),
                ]
            )

        totals_table_data.extend(
            [
                [
                    Paragraph("Total do médico", styles["totals_label"]),
                    Paragraph(f"R$ {totals['doctor_total']}", styles["totals_amount"]),
                ],
                [
                    Paragraph("Total da clínica", styles["totals_label"]),
                    Paragraph(f"R$ {totals['clinic_total']}", styles["totals_amount"]),
                ],
            ]
        )

        totals_table_data.append(
            [
                Paragraph("Total geral", styles["totals_label_emphasis"]),
                Paragraph(f"R$ {totals['grand_total']}", styles["totals_amount_emphasis"]),
            ]
        )

        table = Table(totals_table_data, colWidths=[55 * mm, 35 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("SPAN", (0, 0), (1, 0)),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
                    ("BACKGROUND", (0, 1), (-1, -2), colors.HexColor("#f9fafb")),
                    ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dbeafe")),
                    ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#cbd5e1")),
                    ("INNERGRID", (0, 1), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ]
            )
        )
        return [table]

    @staticmethod
    def _build_styles():
        """Cria os estilos básicos reutilizados na montagem do PDF."""
        base_styles = getSampleStyleSheet()

        return {
            "company": ParagraphStyle(
                "Company",
                parent=base_styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=15,
                leading=17,
                alignment=1,
                textColor=colors.HexColor("#111827"),
            ),
            "title": ParagraphStyle(
                "Title",
                parent=base_styles["Heading3"],
                fontName="Helvetica-Bold",
                fontSize=12,
                leading=14,
                alignment=1,
                textColor=colors.HexColor("#111827"),
            ),
            "meta_label": ParagraphStyle(
                "MetaLabel",
                parent=base_styles["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=11,
                textColor=colors.HexColor("#111827"),
            ),
            "meta_value": ParagraphStyle(
                "MetaValue",
                parent=base_styles["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                leading=11,
                textColor=colors.HexColor("#374151"),
            ),
            "table_cell": ParagraphStyle(
                "TableCell",
                parent=base_styles["BodyText"],
                fontName="Helvetica",
                fontSize=8,
                leading=10,
                textColor=colors.black,
            ),
            "table_cell_center": ParagraphStyle(
                "TableCellCenter",
                parent=base_styles["BodyText"],
                fontName="Helvetica",
                fontSize=8,
                leading=10,
                alignment=1,
                textColor=colors.black,
            ),
            "table_cell_right": ParagraphStyle(
                "TableCellRight",
                parent=base_styles["BodyText"],
                fontName="Helvetica",
                fontSize=8,
                leading=10,
                alignment=2,
                textColor=colors.black,
            ),
            "totals_title": ParagraphStyle(
                "TotalsTitle",
                parent=base_styles["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=12,
                textColor=colors.HexColor("#111827"),
            ),
            "totals_label": ParagraphStyle(
                "TotalsLabel",
                parent=base_styles["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                leading=11,
                textColor=colors.HexColor("#374151"),
            ),
            "totals_amount": ParagraphStyle(
                "TotalsAmount",
                parent=base_styles["BodyText"],
                fontName="Helvetica",
                fontSize=9,
                leading=11,
                alignment=2,
                textColor=colors.HexColor("#111827"),
            ),
            "totals_label_emphasis": ParagraphStyle(
                "TotalsLabelEmphasis",
                parent=base_styles["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=12,
                textColor=colors.HexColor("#111827"),
            ),
            "totals_amount_emphasis": ParagraphStyle(
                "TotalsAmountEmphasis",
                parent=base_styles["BodyText"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=12,
                alignment=2,
                textColor=colors.HexColor("#111827"),
            ),
        }
