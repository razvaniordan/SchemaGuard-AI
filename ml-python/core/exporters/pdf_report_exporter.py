from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class PDFReportExporter:
    def export(self, report, output_path: str) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        pdf = canvas.Canvas(str(path), pagesize=A4)
        width, height = A4

        y = height - 50

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, y, report.summary.reportName)

        y -= 40
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y, f"Report ID: {report.reportId}")

        y -= 30
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Summary")

        y -= 20
        pdf.setFont("Helvetica", 10)
        pdf.drawString(50, y, f"Total transactions: {report.summary.totalTransactions}")
        y -= 15
        pdf.drawString(50, y, f"Processed transactions: {report.summary.processedTransactions}")
        y -= 15
        pdf.drawString(50, y, f"Total current fees: {report.summary.totalCurrentFees}")
        y -= 15
        pdf.drawString(50, y, f"Total optimized fees: {report.summary.totalOptimizedFees}")
        y -= 15
        pdf.drawString(50, y, f"Estimated savings: {report.summary.estimatedSavings}")
        y -= 15
        pdf.drawString(50, y, f"Anomaly count: {report.summary.anomalyCount}")
        y -= 15
        pdf.drawString(50, y, f"Top recommendation: {report.summary.topRecommendation}")
        y -= 15
        pdf.drawString(50, y, f"Top root cause: {report.summary.topRootCause}")

        y -= 35
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Recommendation Summary")

        pdf.setFont("Helvetica", 9)
        for item in report.recommendationSummary:
            y -= 18
            if y < 60:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 9)

            pdf.drawString(
                50,
                y,
                f"{item.suggestionType} | count={item.count} | impact={item.totalExpectedImpact} | priority={item.priority}",
            )

        y -= 35
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Root Causes")

        pdf.setFont("Helvetica", 9)
        for item in report.rootCauseSummary:
            y -= 18
            if y < 60:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 9)

            pdf.drawString(
                50,
                y,
                f"{item.condition} | score={item.score} | confidence={item.confidence} | model={item.modelVersion}",
            )

        y -= 35
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y, "Anomalies")

        pdf.setFont("Helvetica", 9)
        for item in report.anomalySummary:
            y -= 18
            if y < 60:
                pdf.showPage()
                y = height - 50
                pdf.setFont("Helvetica", 9)

            pdf.drawString(
                50,
                y,
                f"{item.transactionId} | {item.anomalyType} | {item.severity}",
            )

        pdf.save()
        return str(path)