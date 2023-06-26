import json
from pydantic import BaseModel
from importlib import import_module
from pathlib import Path
from typing import Any
from enum import Enum


def snake_to_pascal(s: str):
    return s.replace('_', ' ').title().replace(' ', '')


def get_config(config_filename: str, in_dir: Path | None = None):
    path = Path(config_filename)

    if not path.is_file():
        path = in_dir / config_filename
    if not path.is_file():
        path = Path('config', config_filename)

    with path.open('rt') as f:
        config = json.load(f)

    return config


class Stage(str, Enum):
    readers = 'readers'
    matchers = 'matchers'
    validators = 'validators'
    transformers = 'transformers'
    writers = 'writers'


class SearchOption(BaseModel):
    """
    Stage modules are imported as novel_tools.<package>.<module_name>. Not all modules within a package is
    a stage, and when a module is a stage, it can be distinguished by its name suffix.
    Stages are not part of the module path, but is used for document generation.
    """
    stage: Stage
    package: str
    module_suffix: str


search_options: list[SearchOption] = [
    SearchOption(stage=Stage.readers, package='readers', module_suffix='reader'),
    SearchOption(stage=Stage.matchers, package='processors.matchers', module_suffix='matcher'),
    SearchOption(stage=Stage.validators, package='processors.validators', module_suffix='validator'),
    SearchOption(stage=Stage.transformers, package='processors.transformers', module_suffix='transformer'),
    SearchOption(stage=Stage.writers, package='writers', module_suffix='writer')
]

# A dict that maps from a Stage to another dict, that maps from stage name to its module.
modules: dict[Stage, dict[str, str]] = {}

for option in search_options:
    module_dir = Path('novel_tools', *option.package.split('.'))
    module_names = [path.stem for path in module_dir.iterdir()
                    if path.name.endswith(f'{option.module_suffix}.py')]
    modules[option.stage] = {snake_to_pascal(module_name): f'novel_tools.{option.package}.{module_name}'
                             for module_name in module_names}


def get_classes(stage: Stage, stage_name: str) -> tuple[Any, Any]:
    module_name = modules[stage][stage_name]
    module = import_module(module_name)
    return getattr(module, stage_name), getattr(module, 'Options', None)


def create_stage(stage: Stage, stage_name: str, args):
    stage_module = modules[stage][stage_name]
    stage_class = getattr(import_module(stage_module), stage_name)
    return stage_class(args)


def create_workflow(config: dict, additional_args=None) -> dict[Stage, list]:
    """Generates the workflow of stages from the config."""
    if additional_args is None:
        additional_args = {}

    workflow = {}
    for stage_name, stage_configs in config.items():
        stage = Stage(stage_name)
        workflow[stage] = [create_stage(stage, stage_config['class'], stage_config | additional_args)
                           for stage_config in stage_configs]

    return workflow


def get_all_classes() -> dict[Stage, dict[str, tuple[Any, Any]]]:
    """Gets all classes -- both the stage class itself (for the description) and the options class (for the fields)."""
    options = {}
    for stage, unit_module_dict in modules.items():
        options[stage] = {unit: get_classes(stage, unit) for unit in unit_module_dict.keys()}
    return options
