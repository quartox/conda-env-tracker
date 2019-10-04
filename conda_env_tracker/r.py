"""Installing, updating and removing R packages."""
from conda_env_tracker.errors import RError
from conda_env_tracker.gateways.r import r_install, r_remove, get_r_shell_remove_command
from conda_env_tracker.packages import Packages


class RHandler:
    """Handle interactions with R packages."""

    def __init__(self, env: "Environment"):
        self.env = env

    def install(self, packages: Packages):
        """Install R packages"""
        shell_command = r_install(name=self.env.name, packages=packages)
        self.update_history_install(packages=packages, shell_command=shell_command)
        self.env.export()

    def update_history_install(self, packages: Packages, shell_command: str):
        """Update history for installing R packages."""
        self.env.update_dependencies(update_r_dependencies=True)
        self.env.history.update_packages(
            packages=packages, dependencies=self.env.dependencies, source="r"
        )
        self.env.validate_packages(packages, source="r")
        self.env.history.append(log=shell_command, action=shell_command)

    def update_history_remove(self, packages: Packages):
        """"Update history for removing R packages."""
        self.env.update_dependencies(update_r_dependencies=True)
        self.env.history.remove_packages(
            packages=packages, dependencies=self.env.dependencies, source="r"
        )
        self.env.validate_packages(source="r")
        remove_command = get_r_shell_remove_command(packages=packages)
        self.env.history.append(log=remove_command, action=remove_command)

    def remove(self, packages: Packages):
        """R remove packages."""
        self._check_dependencies(packages=packages)
        r_remove(name=self.env.name, package=packages)
        self.env.update_dependencies(update_r_dependencies=True)
        self.update_history_remove(packages=packages)
        self.env.export()

    def _check_dependencies(self, packages: Packages):
        """Check dependencies before running R remove."""
        missing_package_names = []
        for package in packages:
            if package.name not in self.env.dependencies.get("r", {}):
                missing_package_names.append(package.name)
        if missing_package_names:
            raise RError(
                f"Could not find R packages {missing_package_names} in {self.env.name}."
            )
