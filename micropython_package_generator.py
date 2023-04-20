import json
import pathlib
from os import path

REPOSITORY_BASE="github:pavlot/pyrftdi.git@RPPico" #TODO Make branch here
PACKAGE_FOLDER="pyRFTdi"
SRC_PACKAGE_FOLDER = path.join("src",PACKAGE_FOLDER)
dict_package = {
    "urls":{},
    "deps":["logging"],
    "version":"0.0.1"
}

src_package_path = pathlib.Path(SRC_PACKAGE_FOLDER)
for file in src_package_path.rglob("*"):
    clean_path = pathlib.Path(file).relative_to(src_package_path)
    dict_package["urls"][str(pathlib.Path(PACKAGE_FOLDER,clean_path))]="{}/{}/{}".format(REPOSITORY_BASE,SRC_PACKAGE_FOLDER,clean_path)

print(json.dumps(dict_package))