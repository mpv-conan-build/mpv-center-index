from conan import ConanFile
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.files import copy, get, rmdir
from conan.tools.apple import is_apple_os
from conan.tools.microsoft import is_msvc
from conan.tools.layout import basic_layout
from conan.tools.gnu import PkgConfigDeps
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0.0"

class LibmpvConan(ConanFile):
    name = "libmpv"
    license = ("GPL-2.0-or-later", "LGPL-2.1-or-later")
    homepage = "https://mpv.io"
    url = "https://github.com/mpv-player/mpv"
    description = "Command line video player"
    topics = ("video", "audio", "player", "multimedia")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        # Basic options
        "shared": [True, False],
        "cplayer": [True, False],
        "tests": [True, False],
        "fuzzers": [True, False],
        "build_date": [True, False],
        "gpl": [True, False],
        "ta_leak_report": [True, False],

        # Features
        "cdda": [True, False],
        "cplugins": [True, False],
        "dvbin": [True, False],
        "dvdnav": [True, False],
        "iconv": [True, False], 
        "javascript": [True, False],
        "jpeg": [True, False],
        "lcms2": [True, False],
        "libarchive": [True, False],
        "libavdevice": [True, False],
        "libbluray": [True, False],
        "lua": ["lua-5.2", "lua-5.1", "luajit", True, False],
        "pthread_debug": [True, False],
        "rubberband": [True, False],
        "sdl2": [True, False],
        "sdl2_gamepad": [True, False],
        "uchardet": [True, False],
        "uwp": [True, False],
        "vapoursynth": [True, False],
        "vector": [True, False],
        "win32_threads": [True, False],
        "zimg": [True, False],
        "zlib": [True, False],

        # Audio outputs
        "alsa": [True, False],
        "audiounit": [True, False],
        "avfoundation": [True, False],
        "coreaudio": [True, False],
        "jack": [True, False],
        "openal": [True, False],
        "opensles": [True, False],
        "oss_audio": [True, False],
        "pipewire": [True, False],
        "pulse": [True, False],
        "sdl2_audio": [True, False],
        "sndio": [True, False],
        "wasapi": [True, False],

        # Video outputs
        "caca": [True, False],
        "cocoa": [True, False],
        "d3d11": [True, False],
        "direct3d": [True, False],
        "dmabuf_wayland": [True, False],
        "drm": [True, False],
        "egl": [True, False],
        "egl_android": [True, False],
        "egl_angle": [True, False],
        "egl_angle_lib": [True, False],
        "egl_angle_win32": [True, False],
        "egl_drm": [True, False],
        "egl_wayland": [True, False],
        "egl_x11": [True, False],
        "gbm": [True, False],
        "gl": [True, False],
        "gl_cocoa": [True, False],
        "gl_dxinterop": [True, False],
        "gl_win32": [True, False],
        "gl_x11": [True, False],
        "plain_gl": [True, False],
        "sdl2_video": [True, False],
        "shaderc": [True, False],
        "sixel": [True, False],
        "spirv_cross": [True, False],
        "vaapi": [True, False],
        "vaapi_drm": [True, False],
        "vaapi_wayland": [True, False],
        "vaapi_win32": [True, False],
        "vaapi_x11": [True, False],
        "vdpau": [True, False],
        "vdpau_gl_x11": [True, False],
        "vulkan": [True, False],
        "wayland": [True, False],
        "x11": [True, False],
        "xv": [True, False],

        # Hardware acceleration
        "android_media_ndk": [True, False],
        "cuda_hwaccel": [True, False],
        "cuda_interop": [True, False],
        "d3d_hwaccel": [True, False],
        "d3d9_hwaccel": [True, False],
        "gl_dxinterop_d3d9": [True, False],
        "ios_gl": [True, False],
        "videotoolbox_gl": [True, False],
        "videotoolbox_pl": [True, False],

        # macOS features
        "macos_10_15_4_features": [True, False],
        "macos_11_features": [True, False],
        "macos_11_3_features": [True, False],
        "macos_12_features": [True, False],
        "macos_cocoa_cb": [True, False],
        "macos_media_player": [True, False],
        "macos_touchbar": [True, False],
        "swift_build": [True, False],

        # Windows features
        "win32_smtc": [True, False],

        # Documentation
        "html_build": [True, False],
        "manpage_build": [True, False],
        "pdf_build": [True, False],
    }
    default_options = {
        # Library options
        "shared": False,

        # Build options
        "gpl": True,
        "build_date": True,

        # Executables
        "cplayer": False,

        # Tests and fuzzers
        "tests": False,
        "fuzzers": False,

        # Debugging
        "ta_leak_report": False,
        "pthread_debug": False,

        # Documentation
        "html_build": False,
        "manpage_build": False,
        "pdf_build": False,
    }
    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        basic_layout(self)

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("MSVC is not supported")
    
    def config_options(self):
        if self.settings.os != "Windows":
            for opt in ["uwp", "wasapi", "win32_threads", "win32_smtc", "d3d11",
                       "d3d_hwaccel", "d3d9_hwaccel", "gl_dxinterop",
                       "gl_dxinterop_d3d9", "direct3d", "gl_win32",
                       "egl_angle", "egl_angle_lib", "egl_angle_win32",
                       "vaapi_win32", "shaderc", "spirv_cross"]:
                delattr(self.options, opt)

        if self.settings.os != "Linux" and self.settings.os != "FreeBSD":
            for opt in ["alsa", "jack", "oss_audio", "pipewire", "pulse", "sndio",
                       "drm", "gbm", "egl_drm", "vaapi_drm", "vaapi_x11", "vaapi_wayland",
                       "vdpau", "vdpau_gl_x11", "x11", "xv", "wayland",
                       "dmabuf_wayland", "egl_wayland", "egl_x11", "gl_x11"]:
                delattr(self.options, opt)
        
        if self.settings.os not in ("Linux", "FreeBSD", "Windows"):
            for opt in ["vaapi"]:
                delattr(self.options, opt)

        if self.settings.os != "Android":
            for opt in ["opensles", "egl_android", "android_media_ndk"]:
                delattr(self.options, opt)

        if not is_apple_os(self):
            # Remove common Apple-specific options
            for opt in ["coreaudio", "avfoundation", "audiounit", "swift_build",
                       "videotoolbox_gl", "videotoolbox_pl"]:
                delattr(self.options, opt)

        if self.settings.os != "iOS":
            # Remove iOS-specific options
            for opt in ["ios_gl"]:
                delattr(self.options, opt)
        if self.settings.os != "Macos":
            # Remove macOS-specific options
            for opt in ["cocoa", "gl_cocoa",
                        "macos_cocoa_cb", "macos_media_player", "macos_touchbar",
                        "macos_10_15_4_features", "macos_11_features",
                        "macos_11_3_features", "macos_12_features"]:
                delattr(self.options, opt)

    def configure(self):
        # Universal defaults first - these apply across all platforms unless overridden
        universal_defaults = {
            "cplayer": True,
            "cplugins": True,

            # Effects
            "rubberband": False, # No conan package available
            "lcms2": True,

            # Formats
            "dvbin": False,
            "dvdnav": False,
            "libbluray": False,
            "cdda": False,
            "vapoursynth": False,
            "jpeg": True,
            "sixel": False,
            "zimg": True,
            "zlib": True,
            "libarchive": True,

            # Scripting
            "javascript": True,
            "lua": "lua-5.2",
            
            # FFmpeg
            "libavdevice": True,

            # Text encoding
            "iconv": True,
            "uchardet": True,

            # CPU features
            "vector": True,

            # SDL2
            "sdl2": True,
            "sdl2_gamepad": True,
            "sdl2_video": True,
            "sdl2_audio": True,

            # Graphics APIs
            "gl": True,
            "egl": False,
            "vulkan": True,

            # Video outputs
            "plain_gl": True,
            "caca": False,

             # Hardware specific acceleration
            "cuda_hwaccel": False,
            "cuda_interop": False,
        }

        # First set universal defaults
        for option, value in universal_defaults.items():
            if self.options.get_safe(option) == None:
                setattr(self.options, option, value)

        # OS-specific defaults
        if self.settings.os == "Windows":
            if self.options.get_safe("shaderc") == None:
                if self.options.get_safe("spirv_cross") in (False, None):
                    self.options.shaderc = True
                    self.options.spirv_cross = False
                else:
                    self.options.shaderc = False
            else:
                if self.options.get_safe("shaderc") == False:
                    self.options.shaderc = False
                    self.options.spirv_cross = True
                else:
                    self.options.spirv_cross = False

            windows_defaults = {
                "uwp": False,
                "wasapi": True,
                "openal": True,
                "win32_threads": True,
                "win32_smtc": True,
                "d3d11": True,
                "d3d_hwaccel": True,
                "d3d9_hwaccel": True,
                "direct3d": True,
                "gl_win32": True,
                "gl_dxinterop": True,
                "gl_dxinterop_d3d9": True,
                "egl": False,
                "egl_angle": False,
                "egl_angle_lib": False,
                "egl_angle_win32": False,
                "vaapi_win32": False,
            }
            for option, value in windows_defaults.items():
                if self.options.get_safe(option) == None:
                    setattr(self.options, option, value)

        elif self.settings.os == "Linux" or self.settings.os == "FreeBSD":
            linux_defaults = {
                "alsa": True,
                "jack": True,
                "oss_audio": True,
                "pipewire": True,
                "pulse": True,
                "sndio": True,
                "openal": True,
                "drm": True,
                "gbm": True,
                "egl": True,
                "egl_drm": True,
                "vaapi": True,
                "vaapi_x11": True,
                "vaapi_wayland": True,
                "vaapi_drm": True,
                "vdpau": True,
                "vdpau_gl_x11": True,
                "x11": True,
                "xv": True,
                "wayland": True,
                "dmabuf_wayland": True,
                "egl": True,
                "egl_wayland": True,
                "egl_x11": True,
                "gl_x11": True,
            }
            for option, value in linux_defaults.items():
                if self.options.get_safe(option) == None:
                    setattr(self.options, option, value)

        elif self.settings.os == "Android":
            android_defaults = {
                "opensles": True,
                "openal": False, # Doesn't work
                "egl": True,
                "egl_android": True,
                "android_media_ndk": True,
            }
            for option, value in android_defaults.items():
                if self.options.get_safe(option) == None:
                    setattr(self.options, option, value)

        elif is_apple_os(self):
            apple_defaults = {
                "audiounit": True,
                "coreaudio": True,
                "avfoundation": True,
                "openal": True,
                "videotoolbox_gl": True,
                "videotoolbox_pl": True,
            }
            for option, value in apple_defaults.items():
                if self.options.get_safe(option) == None:
                    setattr(self.options, option, value)
            
            if self.settings.os == "iOS":
                ios_defaults = {
                    "swift_build": True,
                    "ios_gl": True,
                }
                for option, value in ios_defaults.items():
                    if self.options.get_safe(option) is None:
                        setattr(self.options, option, value)

            elif self.settings.os == "Macos":
                macos_defaults = {
                    "cocoa": True,
                    "gl_cocoa": True,
                    "macos_cocoa_cb": True,
                    "macos_media_player": True,
                    "macos_touchbar": True,
                    "swift_build": True,
                    "macos_10_15_4_features": True,
                    "macos_11_features": True,
                    "macos_11_3_features": True,
                    "macos_12_features": True,
                }
            for option, value in macos_defaults.items():
                if self.options.get_safe(option) is None:
                    setattr(self.options, option, value)

    def build_requirements(self):
        self.tool_requires("meson/[>=1.5]")
        self.tool_requires("pkgconf/[>=2.0.0]")

    def requirements(self):
        # Core dependencies
        self.requires("ffmpeg/[>=6.0.0]")
        self.requires("libass/[>=0.12.2]")
        self.requires("libplacebo/[>=6.338.2]", options={
            "dovi": True,
            "lcms": self.options.get_safe("lcms2"),
            "vulkan": self.options.get_safe("vulkan"),
            "opengl": self.options.get_safe("gl"),
            "d3d11": self.options.get_safe("d3d11"),
        })
        
        # Disc/Stream formats
        if self.options.get_safe("cdda"):
            self.requires("libcdio/[>=0.90]")
            self.requires("libcdio_paranoia/[>=0.90]")
        
        if self.options.get_safe("dvdnav"):
            self.requires("libdvdnav/[>=4.2.0]")
            self.requires("libdvdread/[>=4.1.0]")

        # Graphics APIs and hardware acceleration
        if self.options.get_safe("vulkan"):
                self.requires("vulkan-loader/[>=1.3.238]")
        
        if self.options.get_safe("shaderc"):
            self.requires("shaderc/[>=2023.7]")
        
        if self.options.get_safe("spirv_cross"):
            self.requires("spirv-cross/[>=1.3.268]")

        # X11 and related
        if self.options.get_safe("x11"):
            self.requires("xorg/system")
            
        # OpenGL and EGL
        if self.options.get_safe("gl"):
            self.requires("opengl/system")
                
        if self.options.get_safe("egl"):
            self.requires("egl/system")
            
        # Audio outputs
        if self.options.get_safe("alsa"):
            self.requires("libalsa/[>=1.0.18]")
        
        if self.options.get_safe("jack"):
            self.requires("jack2/[>=0.0.1]")
        
        if self.options.get_safe("pulse"):
            self.requires("pulseaudio/[>=1.0]")
        
        if self.options.get_safe("sndio"):
            self.requires("sndio/[>=1.9.0]")

        if self.options.get_safe("pipewire"):
            self.requires("libpipewire/[>=0.3.57]")
        if self.options.get_safe("openal"):
            if self.settings.os == "Android":
                self.requires("oboe/[>=1.5.0]")
            self.requires("openal-soft/[>=1.22.0]")

            
        # Video outputs and hardware acceleration
        if self.options.get_safe("vaapi"):
            self.requires("libva/[>=1.1.0]")
        
        if self.options.get_safe("vdpau"):
            self.requires("libvdpau/[>=0.2]")
        
        if self.options.get_safe("wayland"):
            self.requires("wayland/[>=1.21.0]")
            self.requires("wayland-protocols/[>=1.31]")
            self.requires("xorg/[>=0.3.0]")
        
        if self.options.get_safe("drm"):
            self.requires("libdrm/[>=2.4.105]")
            self.requires("libdisplay-info/[>=0.1.1]")
            
        if self.options.get_safe("gbm"):
            self.requires("opengl/system")

        # SDL2
        if self.options.get_safe("sdl2"):
            self.requires("sdl/[>=2.0.14 <3]")
        
        # Additional features
        if self.options.get_safe("javascript"):
            self.requires("mujs/[>=1.0.0]")
        
        if self.options.get_safe("lcms2"):
            self.requires("lcms/[>=2.6]")
        
        if self.options.get_safe("libarchive"):
            self.requires("libarchive/[>=3.4.0]", 
                          options={"with_iconv": bool(self.options.iconv)}) # Workaround build issue
        
        if self.options.get_safe("libbluray"):
            self.requires("libbluray/[>=0.3.0]")
        
        if self.options.get_safe("lua") != None:
            match self.options.lua:
                case "lua-5.1":
                    self.requires("lua/[>=5.1.0 <5.2.0]")
                case "lua-5.2":
                    self.requires("lua/[>=5.2.0 <5.3.0]")
                case"luajit":
                    self.requires("luajit")
                case True:
                    self.requires("lua/[>=5.1.0 <=5.2.0]")

        # Misc libraries
        if self.options.get_safe("iconv") and self.settings.os != "Linux" and self.settings.os != "Android":
            self.requires("libiconv/[>=1.17]")
            
        if self.options.get_safe("jpeg"):
            self.requires("libjpeg/[>=9]")
            
        if self.options.get_safe("zlib"):
            self.requires("zlib/[>=1.2.11]")
            
        if self.options.get_safe("zimg"):
            self.requires("zimg/[>=2.9]")
            
        if self.options.get_safe("uchardet"):
            self.requires("uchardet/[>=0.0.1]")
            
        if self.options.get_safe("vapoursynth"):
            self.requires("vapoursynth/[>=56]")
            self.requires("vapoursynth-script/[>=56]")

        # Additional outputs    
        if self.options.get_safe("caca"):
            self.requires("libcaca/[>=0.99]")
            
        if self.options.get_safe("sixel"):
            self.requires("libsixel/[>=1.5]")

    def generate(self):
        pc = PkgConfigDeps(self)
        pc.generate()
        
        tc = MesonToolchain(self)
        # Hard coded options
        tc.project_options["libmpv"] = "true"

        # Set boolean meson options based on conan options
        boolean_options ={
            "cplayer": "cplayer",
            "tests": "tests",
            "fuzzers": "fuzzers",
            "build-date": "build_date",
            "gpl": "gpl",
            "ta-leak-report": "ta_leak_report", 
        } 
        tc.project_options.update({
            option : ("true" if self.options.get_safe(value) else "false")
                for option, value in boolean_options.items()
        })
        
        # Features from meson.options
        feature_options = {
            "cdda": "cdda",
            "cplugins": "cplugins",
            "dvbin": "dvbin",
            "dvdnav": "dvdnav",
            "iconv": "iconv",
            "javascript": "javascript",
            "jpeg": "jpeg",
            "lcms2": "lcms2",
            "libarchive": "libarchive",
            "libavdevice": "libavdevice",
            "libbluray": "libbluray",
            "lua": "lua",
            "pthread-debug": "pthread_debug",
            "rubberband": "rubberband",
            "sdl2": "sdl2",
            "sdl2-gamepad": "sdl2_gamepad",
            "uchardet": "uchardet",
            "uwp": "uwp",
            "vapoursynth": "vapoursynth",
            "vector": "vector",
            "win32-threads": "win32_threads",
            "zimg": "zimg",
            "zlib": "zlib",

            # Audio outputs
            "alsa": "alsa",
            "audiounit": "audiounit",
            "coreaudio": "coreaudio",
            "avfoundation": "avfoundation",
            "jack": "jack",
            "openal": "openal",
            "opensles": "opensles",
            "oss-audio": "oss_audio",
            "pipewire": "pipewire",
            "pulse": "pulse",
            "sdl2-audio": "sdl2_audio",
            "sndio": "sndio",
            "wasapi": "wasapi",

            # Video outputs and features
            "caca": "caca",
            "cocoa": "cocoa",
            "d3d11": "d3d11",
            "direct3d": "direct3d",
            "dmabuf-wayland": "dmabuf_wayland",
            "drm": "drm",
            "egl": "egl",
            "egl-android": "egl_android",
            "egl-angle": "egl_angle",
            "egl-angle-lib": "egl_angle_lib",
            "egl-angle-win32": "egl_angle_win32",
            "egl-drm": "egl_drm",
            "egl-wayland": "egl_wayland",
            "egl-x11": "egl_x11",
            "gbm": "gbm",
            "gl": "gl",
            "gl-cocoa": "gl_cocoa",
            "gl-dxinterop": "gl_dxinterop",
            "gl-win32": "gl_win32",
            "gl-x11": "gl_x11",
            "plain-gl": "plain_gl",
            "sdl2-video": "sdl2_video",
            "shaderc": "shaderc",
            "sixel": "sixel",
            "spirv-cross": "spirv_cross",
            "vaapi": "vaapi",
            "vdpau": "vdpau",
            "vdpau-gl-x11": "vdpau_gl_x11",
            "vulkan": "vulkan",
            "wayland": "wayland",
            "x11": "x11",
            "xv": "xv",

            # Hardware acceleration 
            "android-media-ndk": "android_media_ndk",
            "cuda-hwaccel": "cuda_hwaccel",
            "cuda-interop": "cuda_interop",
            "d3d-hwaccel": "d3d_hwaccel",
            "d3d9-hwaccel": "d3d9_hwaccel",
            "gl-dxinterop-d3d9": "gl_dxinterop_d3d9",
            "ios-gl": "ios_gl",
            "videotoolbox-gl": "videotoolbox_gl",
            "videotoolbox-pl": "videotoolbox_pl",

            # macOS features
            "macos-10-15-4-features": "macos_10_15_4_features",
            "macos-11-features": "macos_11_features",
            "macos-11-3-features": "macos_11_3_features",
            "macos-12-features": "macos_12_features",
            "macos-cocoa-cb": "macos_cocoa_cb",
            "macos-media-player": "macos_media_player",
            "macos-touchbar": "macos_touchbar",
            "swift-build": "swift_build",

            # Windows features
            "win32-smtc": "win32_smtc",

            # Documentation
            "html-build": "html_build",
            "manpage-build": "manpage_build",
            "pdf-build": "pdf_build",
        }

        tc.project_options.update({ 
            option : ("enabled" if self.options.get_safe(value) else "disabled")
                for option, value in feature_options.items() 
        })   
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        meson = Meson(self)
        meson.install()
        
        # Copy the license files
        copy(self, pattern="LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="Copyright", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        
        # Remove pkg-config files if static
        if not self.options.shared:
            rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
                 
        if is_apple_os(self) and self.settings.os != "iOS":
            if self.options.swift:
                # Copy Swift module files
                copy(self, "*.swiftmodule", dst=os.path.join(self.package_folder, "lib"), 
                     src=self.build_folder, keep_path=True)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "mpv")
        self.cpp_info.libs = ["mpv"]
            
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["m", "dl", "pthread"])
        
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend([
                "ole32", "user32", "gdi32", "uuid", "ntdll", "avrt", "dwmapi",
                "shcore", "pathcch", "imm32", "uxtheme", "version"
            ])
        
        if self.settings.os == "Android":
            self.cpp_info.system_libs.extend(["android", "log"])
            if self.options.get_safe("android_media_ndk"):
                self.cpp_info.system_libs.extend(["mediandk"])
                
        if is_apple_os(self):
            frameworks = ["CoreFoundation", "Foundation"]
            
            # Common media frameworks
            if self.options.get_safe("videotoolbox_gl") or self.options.get_safe("videotoolbox_pl"):
                frameworks.extend(["CoreVideo", "VideoToolbox"])
                
            if self.options.get_safe("coreaudio"):
                frameworks.extend(["CoreAudio", "AudioToolbox", "AudioUnit"])
                
            if self.options.get_safe("avfoundation"):
                frameworks.extend(["AVFoundation", "CoreMedia"])
                
            # Graphics frameworks
            if self.options.get_safe("gl") or self.options.get_safe("gl_cocoa"):
                frameworks.append("OpenGL")
                
            if self.options.get_safe("cocoa"):
                frameworks.extend(["Cocoa", "IOKit", "QuartzCore"])
            
            # Platform specific
            if self.settings.os == "iOS":
                frameworks.extend(["UIKit", "CoreGraphics"])
                if self.options.get_safe("ios_gl"):
                    frameworks.append("OpenGLES")
            elif self.settings.os == "Macos":
                frameworks.extend(["AppKit", "CoreGraphics"])
                if self.options.get_safe("macos_media_player"):
                    frameworks.append("MediaPlayer")
                if self.options.get_safe("swift"):
                    frameworks.append("SwiftUI")

            self.cpp_info.frameworks.extend(frameworks)