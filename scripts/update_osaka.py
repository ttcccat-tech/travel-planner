#!/usr/bin/env python3
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["REGION"] = "osaka"
from update_attractions import main
main()
