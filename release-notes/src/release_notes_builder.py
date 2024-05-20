import jinja2

from html_to_dict import get_issue_list
from union_data import return_jira_issues, data_union


def render_html_from_template(template_file: str, output_item: dict) -> str:
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_file)
    return template.render(output_item=output_item)


def create_release_notes_html(
    template_file="./src/template.html",
    output_html_file="./data/release_notes_zendesk.html",
):
    output_item = create_union_data_from_files()

    # create final release note html file to post to zendesk
    with open(output_html_file, "w") as fh:
        fh.write(render_html_from_template(template_file, output_item))


def create_union_data_from_files(
    html_data="./data/zendesk_data.html", file_path="./data/jira_data_temp.json"
) -> dict:
    zendesk_data = get_issue_list(html_data)
    jira_data = return_jira_issues(file_path)
    output_item = data_union(zendesk_data, jira_data)
    return output_item


if __name__ == "__main__":
    create_release_notes_html()
