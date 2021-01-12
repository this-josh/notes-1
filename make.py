from pathlib import Path
from tqdm import tqdm
from nbconvert import MarkdownExporter

content_path = Path("content")

all_nb = [
    ipynb_file
    for ipynb_file in content_path.rglob("*.ipynb")
    if ".ipynb_checkpoints" not in ipynb_file.parts
]
all_nb.extend([md_file for md_file in content_path.rglob("*.md")])

md_exporter = MarkdownExporter()

for f in tqdm(all_nb):
    this_dir = "content" / Path(*f.parts[1:-1])

    if f.suffix == ".ipynb":
        # Read in notebooks takes majority of time
        file_content, resources = md_exporter.from_filename(f)
    else:
        with open(f, "r") as md_file:
            file_content = md_file.read()
        resources_path = f.with_suffix("")
        resources = {"outputs": {}}
        if resources_path.is_dir():
            for resource_file in resources_path.glob("*"):
                with open(resource_file, "rb") as resource_data:
                    resources["outputs"][resource_file.name] = resource_data.read()

    if not this_dir.exists():
        this_dir.mkdir(parents=True)

    this_page = this_dir / f.stem
    this_page.with_suffix(".md").write_text(file_content)

    # Do resources exist
    if len(resources["outputs"]) != 0:
        res_names = list(resources["outputs"].keys())
        this_page.mkdir(exist_ok=True)
        for res_name in res_names:
            # Save each resource
            (this_page / res_name).write_bytes(resources["outputs"][res_name])
