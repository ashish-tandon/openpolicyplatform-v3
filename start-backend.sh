#!/bin/bash
echo "Starting Open Policy Backend..."
cd backend/OpenPolicyAshBack
source venv/bin/activate
python manage.py run
