#!/bin/bash
# mkdir -p $DB_DIR
streamlit run HOME.py --server.port=8505 --server.baseUrlPath=/bngblaster/  --server.address=0.0.0.0
