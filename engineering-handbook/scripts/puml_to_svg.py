import os
import shutil
from pathlib import Path, PurePosixPath
import re
from datetime import datetime
import pandas as pd

ROOT_DIR = Path(__file__).absolute().parents[1]


def get_diagram_attributes(file_path, dir, content):
    """ Return list of diagram attributes

    :param file_path: Path to the diagram file
    :param dir:       Folder where all diagrams stored
    :param content:   Content of diagram file
    :return:          List of diagrams attributes,
                      include: path                - path to the file related to dir,
                               file_name           - file name without suffix,
                               puml_file_name      - file name with puml extension,
                               svg_file_name       - file name of generated svg file
                               site_page_file_name - file name of site page where diagram will be located
                               type                - type of diagram(data, data-flow, data-model)
                               domain_name         - domain name, derived as parent folder of diagrams
                               title               - title for generated site page
                               links               - list of paths used as links inside diagram to other diagrams
    """
    path = str(PurePosixPath(file_path).relative_to(dir).parent).replace("domains/", "")
    file_name = file_path.stem
    puml_file_name = file_path.name
    svg_file_name = file_path.stem + ".svg"
    site_page_file_name = file_path.stem + ".md" if puml_file_name != "main.puml" and not puml_file_name.startswith(
        '_main') else "_index.md"
    type = file_path.parent.stem
    domain_name = file_path.parents[1].stem
    title = file_path.stem.replace("-", " ").replace("_", " ").title()
    if puml_file_name.startswith('_main') and "short" not in puml_file_name:
        title = title.replace(' Main', '')
    links = re.findall("\[\[(.*\.puml).*\]\]", content)
    links = [Path(x).name for x in links]
    return [path, file_name, puml_file_name, svg_file_name, site_page_file_name, type, domain_name, title, links]


def process_diagrams(source_dir, target_dir):
    """ Proccess digram files.
        Include next steps: - Copy diagrams to static folder
                            - Change links inside diagrams to refer to site pages
                            - Generate svg files for each diagram
                            - Remove unused folders and file from static folder
                            - Create Data Frame with list of diagrams and they attributes

    :param source_dir: Folder where diagrams originally located
    :param target_dir: Forder in static, where diagrams images should be located
    :return: Data Frame with list of diagrams and they attributes
    """

    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)

    diagrams_list = []
    files_paths = sorted(target_dir.glob("**/*.puml"))
    for file_path in files_paths:
        with open(file_path, 'r') as file:
            content = file.read()
        diagrams_list.append(get_diagram_attributes(file_path, target_dir, content))
        content = re.sub('\[\[(.*)/[_]main.*/.puml(.*)\]\]', r'[[\1/\2]]', content, flags=re.M)
        content = re.sub('\[\[(.*).puml(.*)\]\]', r'[[\1/\2]]', content, flags=re.M)
        with open(file_path, 'w') as file:
            file.write(content)

    os.system(f"java -jar {ROOT_DIR}/lib/plantuml.jar -v -tsvg -r '{target_dir}**.puml'")

    shutil.copytree(target_dir / "domains", target_dir, dirs_exist_ok=True)

    for file_path in sorted(target_dir.glob("**/*.puml")):
        os.remove(file_path)

    for rm_dir in ["domains", "legend", "style"]:
        shutil.rmtree(target_dir / rm_dir, ignore_errors=True)

    diagrams_list_df = pd.DataFrame(diagrams_list,
                                    columns=["path", "file_name", "puml_file_name", "svg_file_name",
                                             "site_page_file_name", "type",
                                             "domain_name", "title", "links"])
    return diagrams_list_df


def generate_data_flows_pages(df, site_dir, date):
    """ Generate site pages for Data Flow diagrams. Does not include Domain conceptual views.
    :param df: Data Frame that contain all diagrams with attributes
    :param site_dir: Path to the site forlder
    :param date: Date in format %Y-%m-%d that need to passed to site page
    :return:
    """
    data_flows_df = df[(df["type"] == "data-flows") & (df["site_page_file_name"] != "_index.md")]
    with open(ROOT_DIR / "scripts/data_flow_template.md") as file:
        template = file.read()
    for index, row in data_flows_df.iterrows():
        if not os.path.exists(site_dir / row["path"]):
            os.makedirs(site_dir / row["path"])
        content = template.format(title=row["title"], date=date, file_path="../" + row["svg_file_name"])
        with open(site_dir / row["path"] / row["site_page_file_name"], 'w+') as file:
            file.write(content)

def generate_data_model_pages(df, site_dir, date):
    """ Generate site pages for Data Model diagrams. Only full view data models for databases generate, short versions are skiped.
    :param df: Data Frame that contain all diagrams with attributes
    :param site_dir: Path to the site folder
    :param date: Date in format %Y-%m-%d that need to passed to site page
    :return:
    """
    data_flows_df = df[(df["type"] == "data-model") & (df["site_page_file_name"] == "_index.md") & (df["puml_file_name"].map(lambda x: "short" not in x))]
    with open(ROOT_DIR / "scripts/data_model_template.md") as file:
        template = file.read()
    for index, row in data_flows_df.iterrows():
        if not os.path.exists(site_dir / row["path"]):
            os.makedirs(site_dir / row["path"])
        content = template.format(title=row["title"], date=date, file_path="../" + row["svg_file_name"])
        with open(site_dir / row["path"] / row["svg_file_name"].replace('.svg', '.md'), 'w+') as file:
            file.write(content)


def generate_entity_pages(df, site_dir, date):
    """ Generate site pages for Entity View.
    :param df: Data Frame that contain all diagrams with attributes
    :param site_dir: Path to the site folder
    :param date: Date in format %Y-%m-%d that need to passed to site page
    :return:
    """
    entity_df = df[(df["type"] == "data-model") & (df["site_page_file_name"] != "_index.md")]
    with open(ROOT_DIR / "scripts/entity_template.md") as file:
        template = file.read()
    for _, row in entity_df.iterrows():
        if not os.path.exists(site_dir / row["path"]):
            os.makedirs(site_dir / row["path"])
        rel_path = "/".join([".." for x in range(len(Path(row["path"]).parents) + 1)])
        data_flows_df = df[(df["type"] == "data-flows") & (df["links"].map(lambda x: row["puml_file_name"] in x))]

        data_flows = "".join(
            [f"""\n - [{_row["title"]}]({rel_path}/{_row["path"]}/{_row["file_name"]}/)""" for _, _row in
             data_flows_df.iterrows()])

        data_samples_df = df[(df["type"] == "data") & (df["puml_file_name"].map(lambda x: re.match(row["file_name"]+"_sample\d*.puml", x)))]
        data_samples = "".join([f"""\n### {_row["title"]}\n\n<object data="{rel_path}/{_row["path"]}/{_row["svg_file_name"]}" type="image/svg+xml"></object>""" for _, _row in
                                data_samples_df.iterrows()])

        content = template.format(title=row["title"], date=date, entity_attributes_svg="../" + row["svg_file_name"],data_flows=data_flows, data_model_svg="", data_samples=data_samples)
        with open(site_dir / row["path"] / row["site_page_file_name"], 'w+') as file:
            file.write(content)

def generate_domain_pages(df, site_dir, date):
    """ Generate site pages for Domain data model.
    :param df: Data Frame that contain all diagrams with attributes
    :param site_dir: Path to the site forlder
    :param date: Date in format %Y-%m-%d that need to passed to site page
    :return:
    """
    with open(ROOT_DIR / "scripts/domain_template.md") as file:
        template = file.read()
    subdirs = [PurePosixPath(path).relative_to(site_dir) for path in site_dir.glob("**/")]
    for domain_dir in subdirs:
        if domain_dir.name in ["data-flows", "data-model", "data"]:
            continue
        if str(domain_dir.name) != "":
            title = domain_dir.name.replace("-", " ").replace("_", " ").title()
            data_flow_path = str(domain_dir) + "/data-flows"
            data_model_path = str(domain_dir) + "/data-model"
        else:
            title = "Data Flows"
            data_flow_path = "data-flows"
            data_model_path = "data-model"
        data_flows_df = df[(df["path"] == data_flow_path) & (df["site_page_file_name"] == "_index.md")]
        data_flows = "\n".join(
            [f"""<object data="data-flows/{_row["svg_file_name"]}" type="image/svg+xml"></object>""" for _, _row in
             data_flows_df.iterrows()])

        data_models_df = df[(df["path"] == data_model_path) & (df["site_page_file_name"] == "_index.md") & (df["puml_file_name"].map(lambda x: "short" in x))]
        data_models = "\n".join(
            [f"""<object data="data-model/{_row["svg_file_name"]}" type="image/svg+xml"></object>""" for _, _row in
             data_models_df.iterrows()])
        content = template.format(title=title, date=date, description="", data_flows=data_flows, data_models=data_models)
        with open(site_dir / domain_dir / "_index.md", 'w+') as file:
            file.write(content)


if __name__ == "__main__":
    # root_dir = Path(__file__).absolute().parents[1]
    source_dir = ROOT_DIR / "data-model-diagrams"
    target_dir = ROOT_DIR / "static/docs/guilds/architecture/data-model/data-flows"
    site_dir = ROOT_DIR / "content/en/docs/Guilds/Architecture/Data Model/Data Flows"

    shutil.rmtree(target_dir, ignore_errors=True)
    shutil.rmtree(site_dir, ignore_errors=True)

    df = process_diagrams(source_dir, target_dir)
    date = datetime.now().strftime("%Y-%m-%d")

    generate_data_flows_pages(df, site_dir, date)
    generate_data_model_pages(df, site_dir, date)
    generate_entity_pages(df, site_dir, date)
    generate_domain_pages(df, site_dir, date)
