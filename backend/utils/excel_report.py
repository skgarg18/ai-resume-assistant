import io
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger
import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


class ExcelReportGenerator:
    """Generates a professional 3-sheet Excel report for Resume AI evaluations strictly in memory."""

    # Color Palette Constants (Executive Navy Theme)
    COLOR_PRIMARY_NAVY = "1F4E78"
    COLOR_SECONDARY_BLUE = "2F5597"
    COLOR_WHITE = "FFFFFF"
    COLOR_LIGHT_GRAY = "F2F2F2"
    COLOR_BORDER_GRAY = "D9D9D9"

    # Score Fill Palette for Conditional Formatting
    COLOR_SCORE_GREEN = "C6EFCE"       # >= 90
    COLOR_SCORE_LIGHT_GREEN = "E2EFDA" # 80-89
    COLOR_SCORE_YELLOW = "FFF2CC"      # 70-79
    COLOR_SCORE_ORANGE = "FCE4D6"      # 60-69
    COLOR_SCORE_RED = "F8CBAD"         # < 60

    FONT_FAMILY = "Calibri"

    def __init__(self, session_data: Dict[str, Any], candidates_data: List[Dict[str, Any]]):
        self.session_id: str = str(session_data.get("session_id") or session_data.get("id", "N/A"))
        self.session_name: str = str(session_data.get("session_name", "N/A"))
        self.job_description: str = session_data.get("job_description", "No Job Description Provided")
        self.export_time_str: str = session_data.get("export_time_str", "N/A")
        
        # Sort candidates descending by top-level overall_score upfront
        self.candidates: List[Dict[str, Any]] = sorted(
            candidates_data,
            key=lambda x: self._extract_overall_score(x),
            reverse=True
        )
        self.wb = openpyxl.Workbook()
        # Remove default sheet
        self.wb.remove(self.wb.active)

    @staticmethod
    def _extract_overall_score(candidate_obj: Any) -> float:
        """Safely extract top-level overall_score metric from candidate dictionary."""
        if isinstance(candidate_obj, dict):
            val = candidate_obj.get("overall_score", 0)
            return float(val) if isinstance(val, (int, float)) else 0.0
        return 0.0

    @staticmethod
    def _extract_score(score_obj: Any, key: str) -> float:
        """Safely extract section score metrics handling missing or malformed score JSON payload."""
        if isinstance(score_obj, dict):
            val = score_obj.get(key, 0)
            return float(val) if isinstance(val, (int, float)) else 0.0
        return 0.0

    def generate(self) -> io.BytesIO:
        """Main execution flow generating the complete workbook in memory."""
        logger.info(f"Starting Excel generation for Session: {self.session_name} (ID: {self.session_id})")
        
        stats = self._calculate_statistics()
        
        self._create_dashboard(stats)
        self._create_summary_sheet()
        self._create_metadata_sheet()
        
        buffer = self._save_to_bytes()
        logger.info(f"Successfully generated Excel workbook in memory. Size: {buffer.getbuffer().nbytes} bytes")
        return buffer

    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculates overall_score aggregations and distribution metrics."""
        total = len(self.candidates)
        if total == 0:
            return {
                "total": 0,
                "avg_overall": 0.0,
                "highest": 0.0,
                "lowest": 0.0,
                "gte_90": 0,
                "gte_80": 0,
                "range_70_79": 0,
                "range_60_69": 0,
                "below_60": 0,
            }

        scores = [self._extract_overall_score(c) for c in self.candidates]
        
        gte_90 = sum(1 for s in scores if s >= 90)
        gte_80 = sum(1 for s in scores if s >= 80)
        range_70_79 = sum(1 for s in scores if 70 <= s < 80)
        range_60_69 = sum(1 for s in scores if 60 <= s < 70)
        below_60 = sum(1 for s in scores if s < 60)

        return {
            "total": total,
            "avg_overall": round(sum(scores) / total, 2),
            "highest": max(scores),
            "lowest": min(scores),
            "gte_90": gte_90,
            "gte_80": gte_80,
            "range_70_79": range_70_79,
            "range_60_69": range_60_69,
            "below_60": below_60,
        }

    # =========================================================================
    # SHEET 1: DASHBOARD
    # =========================================================================
    def _create_dashboard(self, stats: Dict[str, Any]) -> None:
        ws = self.wb.create_sheet(title="Dashboard")
        ws.views.sheetView[0].showGridLines = True

        # Title Block
        ws.merge_cells("A1:F2")
        title_cell = ws["A1"]
        title_cell.value = "Resume Evaluation Report"
        title_cell.font = Font(name=self.FONT_FAMILY, size=18, bold=True, color=self.COLOR_WHITE)
        title_cell.fill = PatternFill(start_color=self.COLOR_PRIMARY_NAVY, end_color=self.COLOR_PRIMARY_NAVY, fill_type="solid")
        title_cell.alignment = Alignment(horizontal="center", vertical="center")

        # Session Information Section
        ws["A4"] = "Session Information"
        ws["A4"].font = Font(name=self.FONT_FAMILY, size=13, bold=True, color=self.COLOR_PRIMARY_NAVY)

        session_info = [
            ("Session Name", self.session_name),
            ("Export Date & Time", self.export_time_str),
            ("Total Candidates", stats["total"]),
            ("Average Overall Score", stats["avg_overall"]),
            ("Highest Score", stats["highest"]),
            ("Lowest Score", stats["lowest"]),
            ("Candidates with Score >=90", stats["gte_90"]),
            ("Candidates with Score >=80", stats["gte_80"]),
            ("Candidates between 70-79", stats["range_70_79"]),
            ("Candidates below 70", stats["below_60"] + stats["range_60_69"]),
        ]

        row = 5
        thin_border = self._get_thin_border()
        for label, val in session_info:
            ws.cell(row=row, column=1, value=label).font = Font(name=self.FONT_FAMILY, bold=True)
            ws.cell(row=row, column=1).fill = PatternFill(start_color=self.COLOR_LIGHT_GRAY, fill_type="solid")
            ws.cell(row=row, column=1).border = thin_border

            val_cell = ws.cell(row=row, column=2, value=val)
            val_cell.font = Font(name=self.FONT_FAMILY)
            val_cell.border = thin_border
            val_cell.alignment = Alignment(horizontal="left" if isinstance(val, str) else "center")
            row += 1

        # Job Description Block
        self._write_job_description(ws, start_row=row + 1)

        # Statistics & Score Distribution Table
        dist_start_row = row + 11
        self._write_statistics(ws, stats, start_row=dist_start_row)
        self._apply_auto_width(ws)

    def _write_job_description(self, ws: Any, start_row: int) -> None:
        """Renders merged, formatted Job Description section."""
        ws.cell(row=start_row, column=1, value="Target Job Description").font = Font(
            name=self.FONT_FAMILY, size=13, bold=True, color=self.COLOR_PRIMARY_NAVY
        )

        jd_start = start_row + 1
        jd_end = start_row + 8
        ws.merge_cells(start_row=jd_start, start_column=1, end_row=jd_end, end_column=6)

        jd_cell = ws.cell(row=jd_start, column=1, value=self.job_description)
        jd_cell.font = Font(name=self.FONT_FAMILY, size=10, italic=True)
        jd_cell.alignment = Alignment(vertical="top", wrap_text=True)

        fill = PatternFill(start_color="FAF8F5", fill_type="solid")
        thin_border = self._get_thin_border()

        for r in range(jd_start, jd_end + 1):
            for c in range(1, 7):
                cell = ws.cell(row=r, column=c)
                cell.fill = fill
                cell.border = thin_border

    def _write_statistics(self, ws: Any, stats: Dict[str, Any], start_row: int) -> None:
        """Renders Score Distribution Table and attaches Bar Chart."""
        ws.cell(row=start_row, column=1, value="Score Distribution").font = Font(
            name=self.FONT_FAMILY, size=13, bold=True, color=self.COLOR_PRIMARY_NAVY
        )

        header_row = start_row + 1
        ws.cell(row=header_row, column=1, value="Score Range")
        ws.cell(row=header_row, column=2, value="Candidates")
        
        fill = PatternFill(start_color=self.COLOR_PRIMARY_NAVY, fill_type="solid")
        font = Font(name=self.FONT_FAMILY, color=self.COLOR_WHITE, bold=True)
        thin_border = self._get_thin_border()
        for col in (1, 2):
            c = ws.cell(row=header_row, column=col)
            c.fill = fill
            c.font = font
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = thin_border

        distribution_data = [
            ("90-100", stats["gte_90"]),
            ("80-89", stats["gte_80"] - stats["gte_90"]),
            ("70-79", stats["range_70_79"]),
            ("60-69", stats["range_60_69"]),
            ("Below 60", stats["below_60"]),
        ]

        curr_row = header_row + 1
        for rng, count in distribution_data:
            c1 = ws.cell(row=curr_row, column=1, value=rng)
            c2 = ws.cell(row=curr_row, column=2, value=count)

            c1.alignment = Alignment(horizontal="center")
            c2.alignment = Alignment(horizontal="center")

            c1.border = thin_border
            c2.border = thin_border
            curr_row += 1

        # Embed Bar Chart
        chart = BarChart()
        chart.type = "col"
        chart.style = 10
        chart.title = "Candidate Score Distribution"
        chart.y_axis.title = "Number of Candidates"
        chart.x_axis.title = "Score Ranges"
        chart.legend = None

        data_ref = Reference(ws, min_col=2, min_row=header_row, max_row=curr_row - 1)
        cats_ref = Reference(ws, min_col=1, min_row=header_row + 1, max_row=curr_row - 1)

        chart.add_data(data_ref, titles_from_data=True)
        chart.set_categories(cats_ref)

        ws.add_chart(chart, f"D{start_row}")

    # =========================================================================
    # SHEET 2: CANDIDATE EVALUATION SUMMARY (MULTI-LEVEL HEADERS)
    # =========================================================================
    def _create_summary_sheet(self) -> None:
        ws = self.wb.create_sheet(title="Candidate Summary")
        ws.views.sheetView[0].showGridLines = True

        main_headers = [
            ("Candidate Profile", 4),
            ("Evaluation Scores", 6),
            ("AI Assessment & Skill Gap", 5)
        ]

        sub_headers = [
            "Rank", "Candidate Name", "Email", "Contact Number",
            "Overall Score", "Domain Relevance", "Project Evidence",
            "Technical Skills", "Education & Training", "Professional Experience",
            "AI Summary", "Recruiter Insights", "Matched Skills", "Missing Skills", "Remarks"
        ]

        self._apply_multilevel_headers(ws, main_headers, sub_headers)
        thin_border = self._get_thin_border()

        for idx, c in enumerate(self.candidates, start=1):
            row_idx = idx + 2  # Data starts at Row 3
            score_dict = c.get("score") if isinstance(c.get("score"), dict) else {}
            basic_info = c.get("basic_info") if isinstance(c.get("basic_info"), dict) else {}

            name = c.get("name") or basic_info.get("name") or "N/A"
            email = c.get("email") or basic_info.get("email") or "N/A"
            contact = c.get("contact") or basic_info.get("contact") or "N/A"

            row_data = [
                idx,  # Auto-generated Rank
                name,
                email,
                contact,
                self._extract_overall_score(c),  # Root variable extraction
                self._extract_score(score_dict, "domain_relevance"),
                self._extract_score(score_dict, "project_evidence"),
                self._extract_score(score_dict, "technical_skills"),
                self._extract_score(score_dict, "education_and_training"),
                self._extract_score(score_dict, "professional_experience"),
                self._list_to_multiline(c.get("summary")),
                self._flatten_recruiter_insights(c.get("recruiter_insights")),
                self._list_to_multiline(c.get("matched_skills")),
                self._list_to_multiline(c.get("missing_skills")),
                ""  # Remarks left blank for manual entries
            ]

            ws.append(row_data)

            fill_color = self.COLOR_LIGHT_GRAY if idx % 2 == 0 else self.COLOR_WHITE
            row_fill = PatternFill(start_color=fill_color, fill_type="solid")

            for col_idx in range(1, len(sub_headers) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.fill = row_fill
                cell.border = thin_border
                cell.font = Font(name=self.FONT_FAMILY)

                if col_idx in [1, 5, 6, 7, 8, 9, 10]:
                    cell.alignment = Alignment(horizontal="center", vertical="top")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

        ws.freeze_panes = "A3"
        ws.auto_filter.ref = f"A2:O{len(self.candidates) + 2}"

        self._apply_conditional_formatting(ws, max_row=len(self.candidates) + 2)
        self._apply_auto_width(ws)

    # =========================================================================
    # SHEET 3: CANDIDATE METADATA (MULTI-LEVEL HEADERS)
    # =========================================================================
    def _create_metadata_sheet(self) -> None:
        ws = self.wb.create_sheet(title="Candidate Metadata")
        ws.views.sheetView[0].showGridLines = True

        main_headers = [
            ("Candidate Overview", 3),
            ("Education Details", 4),
            ("Professional Experience", 4),
            ("Projects & Credentials", 3),
            ("Resume Summary", 1)
        ]

        sub_headers = [
            "Candidate Name", "Core Skills", "Languages",
            "Degree & Specialization", "Institution & Location", "Duration", "Academic Score",
            "Designation & Company", "Duration & Location", "Technologies Used", "Key Responsibilities & Impact",
            "Projects", "Certifications", "Achievements",
            "Full Summary"
        ]

        self._apply_multilevel_headers(ws, main_headers, sub_headers)
        thin_border = self._get_thin_border()

        for idx, c in enumerate(self.candidates, start=1):
            row_idx = idx + 2  # Data starts at Row 3
            basic_info = c.get("basic_info") if isinstance(c.get("basic_info"), dict) else {}

            name = c.get("name") or basic_info.get("name") or "N/A"
            edu_deg, edu_inst, edu_dur, edu_score = self._flatten_education_split(c.get("education"))
            exp_role, exp_dur, exp_tech, exp_desc = self._flatten_experience_split(c.get("experience"))
            
            resume_summary = c.get("resume_summary")
            resume_summary_val = resume_summary.strip() if isinstance(resume_summary, str) and resume_summary.strip() else "N/A"

            row_data = [
                name,
                self._list_to_multiline(c.get("skills")),
                self._list_to_multiline(c.get("languages")),
                edu_deg,
                edu_inst,
                edu_dur,
                edu_score,
                exp_role,
                exp_dur,
                exp_tech,
                exp_desc,
                self._flatten_projects(c.get("projects")),
                self._flatten_certifications(c.get("certifications")),
                self._flatten_achievements(c.get("achievements")),
                resume_summary_val
            ]

            ws.append(row_data)

            for col_idx in range(1, len(sub_headers) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.border = thin_border
                cell.alignment = Alignment(vertical="top", wrap_text=True)
                cell.font = Font(name=self.FONT_FAMILY)

        ws.freeze_panes = "A3"
        ws.auto_filter.ref = f"A2:O{len(self.candidates) + 2}"
        self._apply_auto_width(ws)

    # =========================================================================
    # STYLING & FORMATTING HELPERS
    # =========================================================================
    def _get_thin_border(self) -> Border:
        thin_side = Side(border_style="thin", color=self.COLOR_BORDER_GRAY)
        return Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

    def _apply_multilevel_headers(
        self,
        ws: Any,
        main_headers: List[Tuple[str, int]],
        sub_headers: List[str]
    ) -> None:
        """Applies executive 2-level stacked header structure."""
        primary_fill = PatternFill(start_color=self.COLOR_PRIMARY_NAVY, fill_type="solid")
        primary_font = Font(name=self.FONT_FAMILY, color=self.COLOR_WHITE, bold=True, size=11)

        sub_fill = PatternFill(start_color=self.COLOR_SECONDARY_BLUE, fill_type="solid")
        sub_font = Font(name=self.FONT_FAMILY, color=self.COLOR_WHITE, bold=True, size=10)

        thin_border = self._get_thin_border()

        # Row 1: Merged Category Headers
        curr_col = 1
        for title, span in main_headers:
            end_col = curr_col + span - 1
            if span > 1:
                ws.merge_cells(start_row=1, start_column=curr_col, end_row=1, end_column=end_col)

            for c in range(curr_col, end_col + 1):
                cell = ws.cell(row=1, column=c)
                cell.fill = primary_fill
                cell.border = thin_border

            main_cell = ws.cell(row=1, column=curr_col, value=title)
            main_cell.font = primary_font
            main_cell.alignment = Alignment(horizontal="center", vertical="center")

            curr_col = end_col + 1

        # Row 2: Detailed Sub-headers
        for col_idx, header in enumerate(sub_headers, start=1):
            cell = ws.cell(row=2, column=col_idx, value=header)
            cell.font = sub_font
            cell.fill = sub_fill
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = thin_border

        ws.row_dimensions[1].height = 24
        ws.row_dimensions[2].height = 28

    def _apply_conditional_formatting(self, ws: Any, max_row: int) -> None:
        """Applies score rules dynamically to overall and section score columns (E through J)."""
        if max_row < 3:
            return

        rules = [
            ("90", "1000", self.COLOR_SCORE_GREEN),
            ("80", "89.99", self.COLOR_SCORE_LIGHT_GREEN),
            ("70", "79.99", self.COLOR_SCORE_YELLOW),
            ("60", "69.99", self.COLOR_SCORE_ORANGE),
            ("0", "59.99", self.COLOR_SCORE_RED),
        ]

        target_range = f"E3:J{max_row}"

        for gte, lte, color in rules:
            rule = CellIsRule(
                operator="between",
                formula=[gte, lte],
                fill=PatternFill(start_color=color, end_color=color, fill_type="solid")
            )
            ws.conditional_formatting.add(target_range, rule)

    def _apply_auto_width(self, ws: Any) -> None:
        """Automatically adjusts column widths for optimal legibility."""
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.value:
                    lines = str(cell.value).split("\n")
                    for line in lines:
                        if len(line) > max_len:
                            max_len = len(line)

            adjusted_width = min(max(max_len + 3, 14), 48)
            ws.column_dimensions[col_letter].width = adjusted_width

    # =========================================================================
    # DATA FLATTENING HELPERS WITH 'N/A' SAFEGUARDS
    # =========================================================================
    @staticmethod
    def _list_to_multiline(data: Any) -> str:
        """Converts lists into single cell multi-line string format with N/A fallback."""
        if isinstance(data, list) and data:
            cleaned = [str(item).strip() for item in data if item and str(item).strip()]
            return "\n".join(cleaned) if cleaned else "N/A"
        if isinstance(data, str) and data.strip():
            return data.strip()
        return "N/A"

    @staticmethod
    def _flatten_recruiter_insights(insights_data: Any) -> str:
        """Formats structured recruiter insights with explicit N/A fallbacks."""
        if not isinstance(insights_data, list) or not insights_data:
            return insights_data.strip() if isinstance(insights_data, str) and insights_data.strip() else "N/A"

        blocks = []
        for item in insights_data:
            if isinstance(item, dict):
                insight = item.get("insight") or "N/A"
                category = item.get("category") or "General"
                importance = item.get("importance") or ""
                evidence = item.get("evidence")

                tags = [t for t in [category, f"{importance} Importance" if importance else ""] if t]
                tag_prefix = f"[{' | '.join(tags)}] " if tags else ""

                bullet = f"• {tag_prefix}{insight}"
                if evidence:
                    bullet += f"\n  Evidence: {evidence}"
                blocks.append(bullet)
            elif isinstance(item, str) and item.strip():
                blocks.append(f"• {item.strip()}")

        return "\n\n".join(blocks) if blocks else "N/A"

    @staticmethod
    def _flatten_education_split(edu_data: Any) -> Tuple[str, str, str, str]:
        """
        Splits education across 4 multi-line sub-columns with N/A fallbacks:
        (degree_specialization, institution_location, duration, academic_score)
        """
        if not isinstance(edu_data, list) or not edu_data:
            return "N/A", "N/A", "N/A", "N/A"

        deg_list, inst_list, dur_list, score_list = [], [], [], []

        for item in edu_data:
            if isinstance(item, dict):
                degree = item.get("degree") or ""
                spec = item.get("specialization") or ""
                deg_str = f"{degree} - {spec}" if degree and spec else (degree or spec or "N/A")

                institution = item.get("institution") or ""
                location = item.get("location") or ""
                inst_str = f"{institution}\n({location})" if institution and location else (institution or location or "N/A")

                start_yr = item.get("start_year") or item.get("start_date")
                end_yr = item.get("end_year") or item.get("end_date") or item.get("year")
                duration = f"{start_yr} - {end_yr}" if start_yr and end_yr else str(end_yr or start_yr or item.get("duration") or "N/A")

                acad_score = item.get("academic_score") or item.get("score") or item.get("cgpa") or item.get("grade")
                score_val = "N/A"
                if isinstance(acad_score, dict):
                    score_val = acad_score.get("raw_value") or (
                        f"{acad_score.get('score')} ({acad_score.get('type')})"
                        if acad_score.get("score") and acad_score.get("type")
                        else str(acad_score.get("score") or "N/A")
                    )
                elif acad_score:
                    score_val = str(acad_score)

                deg_list.append(f"• {deg_str}")
                inst_list.append(f"• {inst_str}")
                dur_list.append(f"• {duration}")
                score_list.append(f"• {score_val}")

        return (
            "\n\n".join(deg_list) if deg_list else "N/A",
            "\n\n".join(inst_list) if inst_list else "N/A",
            "\n\n".join(dur_list) if dur_list else "N/A",
            "\n\n".join(score_list) if score_list else "N/A"
        )

    @staticmethod
    def _flatten_experience_split(exp_data: Any) -> Tuple[str, str, str, str]:
        """
        Splits experience across 4 multi-line sub-columns with N/A fallbacks:
        (designation_company, duration_location, tech_stack, responsibilities)
        """
        if not isinstance(exp_data, list) or not exp_data:
            return "N/A", "N/A", "N/A", "N/A"

        desig_comp_list, dur_loc_list, tech_list, desc_list = [], [], [], []

        for item in exp_data:
            if isinstance(item, dict):
                desig = item.get("designation") or item.get("role") or item.get("title") or ""
                comp = item.get("company") or item.get("organization") or ""
                desig_comp = f"{desig} at {comp}" if desig and comp else (desig or comp or "N/A")

                start_d = item.get("start_date") or item.get("start_year") or ""
                end_d = item.get("end_date") or item.get("end_year") or ""
                if item.get("currently_working"):
                    end_d = "Present"
                duration = f"{start_d} - {end_d}" if start_d and end_d else str(end_d or start_d or "")

                loc = item.get("location") or ""
                dur_loc = f"{duration}\n({loc})" if duration and loc else (duration or loc or "N/A")

                techs = item.get("technologies_used") or item.get("tech_stack") or []
                tech_str = ", ".join(str(t) for t in techs if t) if isinstance(techs, list) and techs else "N/A"

                descriptions = item.get("description") or []
                if isinstance(descriptions, list) and descriptions:
                    bullet_desc = "\n".join(f"  - {str(d).strip()}" for d in descriptions if d)
                elif isinstance(descriptions, str) and descriptions.strip():
                    bullet_desc = f"  - {descriptions.strip()}"
                else:
                    bullet_desc = "  - N/A"

                desig_comp_list.append(f"• {desig_comp}")
                dur_loc_list.append(f"• {dur_loc}")
                tech_list.append(f"• {tech_str}")
                desc_list.append(f"• {desig_comp}\n{bullet_desc}")

        return (
            "\n\n".join(desig_comp_list) if desig_comp_list else "N/A",
            "\n\n".join(dur_loc_list) if dur_loc_list else "N/A",
            "\n\n".join(tech_list) if tech_list else "N/A",
            "\n\n".join(desc_list) if desc_list else "N/A"
        )

    @staticmethod
    def _flatten_projects(proj_data: Any) -> str:
        """Formats structured projects list with explicit N/A fallbacks."""
        if not isinstance(proj_data, list) or not proj_data:
            return proj_data.strip() if isinstance(proj_data, str) and proj_data.strip() else "N/A"

        blocks = []
        for item in proj_data:
            if isinstance(item, dict):
                title = item.get("title") or item.get("name") or "N/A"
                tech = item.get("tech_stack") or item.get("technologies") or []
                if isinstance(tech, list):
                    tech_str = ", ".join(str(t) for t in tech if t) or "N/A"
                else:
                    tech_str = str(tech) if tech else "N/A"
                desc = item.get("description") or "N/A"

                blocks.append(f"• {title}\n  Tech: {tech_str}\n  Desc: {desc}")
            elif isinstance(item, str) and item.strip():
                blocks.append(f"• {item.strip()}")

        return "\n\n".join(blocks) if blocks else "N/A"

    @staticmethod
    def _flatten_certifications(cert_data: Any) -> str:
        """Formats certifications list with explicit N/A fallbacks."""
        if not isinstance(cert_data, list) or not cert_data:
            return cert_data.strip() if isinstance(cert_data, str) and cert_data.strip() else "N/A"

        items = []
        for c in cert_data:
            if isinstance(c, dict):
                name = c.get("title") or c.get("name") or c.get("certification") or ""
                issuer = c.get("issuer") or c.get("authority") or ""
                item_str = f"{name} - {issuer}" if issuer and name else (name or issuer or "N/A")
                items.append(f"• {item_str}")
            elif isinstance(c, str) and c.strip():
                items.append(f"• {c.strip()}")

        return "\n".join(items) if items else "N/A"

    @staticmethod
    def _flatten_achievements(achieve_data: Any) -> str:
        """Formats achievements list with explicit N/A fallbacks."""
        if not isinstance(achieve_data, list) or not achieve_data:
            return achieve_data.strip() if isinstance(achieve_data, str) and achieve_data.strip() else "N/A"

        items = [f"• {str(item).strip()}" for item in achieve_data if item and str(item).strip()]
        return "\n".join(items) if items else "N/A"

    def _save_to_bytes(self) -> io.BytesIO:
        """Saves current workbook instance to in-memory BytesIO stream."""
        stream = io.BytesIO()
        self.wb.save(stream)
        stream.seek(0)
        return stream