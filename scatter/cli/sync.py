import importlib.util
from pathlib import Path
from types import FunctionType
from watchfiles import watch
import scatter
from typing import List
from rich.progress import Progress, SpinnerColumn, TextColumn


def get_module(module_name, file_path):
    """
    Load a module from a specific file path.
    """
    try:

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error reloading module {module_name}: {e}")


def get_function_snapshot(module, valid_functions: List[str]):
    """
    Take a snapshot of the functions in the module.
    Returns a dictionary where keys are function names and values are their defining characteristics.
    """
    return {
        name: (getattr(obj, "__code__", None), getattr(obj, "__defaults__", None))
        for name, obj in vars(module).items()
        if isinstance(obj, FunctionType) and name in valid_functions
    }


def compare_function_snapshots(old_snapshot, new_snapshot):
    """
    Compare two snapshots of functions and detect modifications.
    """
    modified_functions = []

    for name, new_info in new_snapshot.items():
        old_info = old_snapshot.get(name)
        if old_info != new_info:
            modified_functions.append(name)

    return modified_functions


def update_functions(module, modified_functions):
    """
    Update the remote functions with the modified functions.
    """
    print(f" Synchronizing endpoints: {modified_functions}")
    for function_name in modified_functions:
        unprocessed_function = getattr(module, function_name)

        processed_function = scatter.track(unprocessed_function)

        processed_function.sync()

    print("Done ✅")


def sync_function_changes(module_name, file_path, old_snapshot, valid_functions: List[str]):
    """
    Reload a module from a specific file path, detect function modifications, and update the remote function.
    """
    
    module = get_module(module_name, file_path)

    # Take a new snapshot of functions and compare
    new_snapshot = get_function_snapshot(module, valid_functions)
    modified_functions = compare_function_snapshots(old_snapshot, new_snapshot)

    # Update the remote functions
    update_functions(module, modified_functions)

    return new_snapshot  # Return the new snapshot for future tracking


def sync_directory(dir_path: str, valid_functions: List[str]):
    """
    Watch a directory for changes and detect modifications in functions.
    """
    resolved_dir_path = Path(dir_path).expanduser().resolve().absolute()
    if not resolved_dir_path.exists():
        raise FileNotFoundError(f"{resolved_dir_path} does not exist")

    # Maintain snapshots for each module
    module_snapshots = {}

    print(f"Watching {resolved_dir_path} for changes...")
    for changes in watch(resolved_dir_path):
        for change_type, changed_file in changes:
            if change_type.raw_str() == "modified" and changed_file.endswith(".py"):
                module_name = Path(changed_file).stem
                print(f"Detected change in {changed_file}")

                # Get the old snapshot (if available)
                old_snapshot = module_snapshots.get(module_name, {})

                # Reload the module and detect changes
                new_snapshot = sync_function_changes(module_name, changed_file, old_snapshot, valid_functions)

                # Update the snapshot for future comparisons
                module_snapshots[module_name] = new_snapshot
