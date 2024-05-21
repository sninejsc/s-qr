import json

from werkzeug import urls

from odoo import http
from odoo.http import request
from odoo.tools.safe_eval import safe_eval, time

from odoo.addons.web.controllers.report import ReportController


class CxReportController(ReportController):
    def _compose_report_file_name(self, docids, report):
        """Compose report file name.
        Uses report name + record name(s) if provided

        Args:
            docids ([Int]): list of record ids
            report (ir.action.report()): report record

        Returns:
            Char: composed name of the report
        """
        report_name = "report"
        if docids:
            records = request.env[report.model].browse(docids)
            record_count = len(docids)
            if record_count == 1:

                # Single record
                report_name = safe_eval(
                    report.sudo().print_report_name, {"object": records, "time": time}
                )
            else:
                # Multiple records
                report_name = f"{report.name} x{record_count}"
        else:
            report_name = report.name
        return report_name

    # ------------------------------------------------------
    # Report controllers
    # ------------------------------------------------------
    @http.route(
        [
            "/report/<converter>/<reportname>",
            "/report/<converter>/<reportname>/<docids>",
        ],
        type="http",
        auth="user",
        website=True,
    )
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter != "pdf":
            return super().report_routes(
                reportname, docids=docids, converter=converter, **data
            )

        report_obj = request.env["ir.actions.report"]
        report = report_obj._get_report_from_name(reportname)
        context = dict(request.env.context)

        # Options
        if data.get("options"):
            data_options = data.pop("options")
            data.update(json.loads(urls.url_unquote_plus(data_options)))

        # Context
        data_context = data.get("context")
        if data_context:
            context.update(json.loads(urls.url_unquote_plus(data_context)))

        # Set allowed companies if provided explicitly
        if data.get("cid"):
            allowed_company_ids = [int(i) for i in data.get("cid").split(",")]
            context.update(allowed_company_ids=allowed_company_ids)

        # Update request context
        request.env.context = context

        # Doc IDs
        if docids:
            docids = [int(i) for i in docids.split(",")]

            # Ensure user has access to the documents
            records = request.env[report.model].browse(docids)
            records.check_access_rule("read")

        report_file_name = self._compose_report_file_name(docids, report)
        pdf = report_obj.with_context(**context)._render_qweb_pdf(
            reportname, docids, data=data
        )[0]
        return request.make_response(
            pdf,
            headers=[
                ("Content-Type", "application/pdf"),
                ("Content-Length", len(pdf)),
                ("Content-Disposition", 'inline; filename="%s.pdf"' % report_file_name),
            ],
        )
