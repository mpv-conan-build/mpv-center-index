from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.layout import basic_layout
from conan.tools.gnu import AutotoolsToolchain
from conan.tools.gnu.get_gnu_triplet import _get_gnu_triplet
from conan.tools.env import Environment

import shlex
from os.path import join
from pathlib import Path
from functools import cached_property

class LibdoviConan(ConanFile):
    name = "libdovi"
    license = "MIT"
    description = "Dolby Vision metadata parsing and writing"
    homepage = "https://github.com/quietvoid/dovi_tool"
    url = "https://github.com/quietvoid/dovi_tool"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "xml": [True, False],
        "serde": [True, False],
    }
    default_options = {
        "shared": False,
        "xml": True,
        "serde": True,
    }

    @cached_property
    def __triplet(self):
        return _get_gnu_triplet(
            str(self.settings.os), 
            str(self.settings.arch), 
            str(self.settings.compiler)
        )['triplet']
    
    @cached_property
    def __cargo_args(self):
        build_type = self.settings.get_safe("build_type", default="Release")
        shared = self.options.shared == True
        

        return [*([] if build_type == 'Debug' else ["-r"]),
            f"--library-type={'cdylib' if shared else 'staticlib'}",
            "-F", 
            "capi" + 
            (",xml" if self.options.xml == True else "") +
            (",serde" if self.options.serde == True else ""),
            "--target", self.__triplet,
            "--target-dir", self.build_folder,
            "--prefix", "/",
            "--destdir", self.package_folder]

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        basic_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def generate(self):
        toolchain = AutotoolsToolchain(self).environment().vars(self)
        env = Environment()
        env.define("RUSTFLAGS", 
            shlex.join(map(lambda flag: f"-Clink-arg={flag}", shlex.split(toolchain["LDFLAGS"]))))
        env.define(f"CARGO_TARGET_{self.__triplet.replace("-", "_").upper()}_LINKER", toolchain["CC"])
        env.vars(self).save_script("rusttoolchain")

    def build(self):
        with Path(self.build_folder, "build.log").open("w") as log:
            self.run(shlex.join((
                    "cargo", "cbuild", 
                    *self.__cargo_args
                )), 
                cwd=join(self.source_folder, "dolby_vision"), 
                stderr=log, 
                env="rusttoolchain"
            )

    def package(self):
        with Path(self.build_folder, "install.log").open("w") as log:
            self.run(shlex.join((
                    "cargo", "cinstall", 
                    *self.__cargo_args
                )), 
                cwd=join(self.source_folder, "dolby_vision"), 
                stderr=log, 
                env="rusttoolchain"
            )
        rmdir(self, join(self.package_folder, "lib", "pkgconfig"))
        copy(self, "LICENSE*", src=self.source_folder, dst=join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "dovi")
        self.cpp_info.libs = ["dovi"]
