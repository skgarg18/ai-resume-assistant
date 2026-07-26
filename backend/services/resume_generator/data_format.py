def convert_data_to_format(resume_metadata):

    resume_data = {
        "name": resume_metadata["basic_info"]["name"],
        "role": resume_metadata["basic_info"]["current_designation"],
        "summary": resume_metadata["resume_summary"],

        "experience": [
            {
                "title": exp["designation"],
                "company": exp["company"],
                "date": f"{exp['start_date']} - {exp['end_date'] or 'Present'}",
                "location": exp["location"],
                "desc": exp["description"],
            }
            for exp in resume_metadata["experience"]
        ],

        "education": [
            {
                "degree": edu["degree"],
                "college": edu["institution"],
                "date": f"{edu['start_year']} - {edu['end_year']}",
                "location": edu["location"],
                "desc": (
                    f"{edu['academic_score']['score']} "
                    f"{edu['academic_score']['type']}"
                    if edu["academic_score"]
                    else None
                ),
            }
            for edu in resume_metadata["education"]
        ],

        "skills": resume_metadata["skills"],

        "footer": {
            "address_1": "2535 Augustine Drive, 5th Floor Santa Clara, CA",
            "address_2": "95054",
            "contact": "Phone: +1-408-273-8900 | www.globallogic.com",
        },
    }

    return resume_data