# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 17:35:58 2022

@author: agust
"""

# -*- coding: utf-8 -*-
from distutils.core import setup
import py2exe

setup(
    name="penalties",
    version="1.0",
    description="Crea un dataset con la velocidad y distancia de penales a partir de .csv exportados en Nacsport",
    author="Agustín Germán Rojas",
    author_email="agustingemanrojas@gmail.com",
    url="url del proyecto",
    license="tipo de licencia",
    scripts=["penales.exe.py"],
    console=["penales.exe.py"],
    options={"py2exe": {"bundle_files": 1}},
    zipfile=None,
)