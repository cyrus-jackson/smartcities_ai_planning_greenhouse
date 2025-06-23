import os
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# Path to the directory containing the template
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__))
PROBLEM_TEMPLATE_FILE = "problem.pddl"
DOMAIN_FILE = "domain.pddl"

# Sample
data = {
    "name": "greenhouse-problem-1",
    "fluents": {"temperature": 25, "humidity": 60},
    "init": ["servo-open s1", "servo-closed s2"],
    "goals": [
        {
            "type": "and",
            "states": ["servo-open s2", "temperature-high temp"]
        }
    ]
}

# Set up Jinja2 environment
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    trim_blocks=True,
    lstrip_blocks=True
)

domain_content = None

def read_file_safe(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def read_domain_data(domain_file=DOMAIN_FILE):
    domain_path = os.path.join(TEMPLATE_DIR, domain_file)
    return read_file_safe(domain_path)

domain_content = read_domain_data() if domain_content == None else domain_content

def get_domain_data():
    return domain_content

def get_problem_file_with_data(unrendered_data=data, template_file=PROBLEM_TEMPLATE_FILE):
    try:
        template = env.get_template(template_file)
        return template.render(data=unrendered_data)
    except TemplateNotFound:
        print(f"Error: Template not found: {template_file}")
        return None
    except Exception as e:
        print(f"Error rendering template {template_file}: {e}")
        return None
