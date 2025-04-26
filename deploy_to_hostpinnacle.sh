#!/bin/bash

# Barberian Deployment Script for HostPinnacle
# This script builds, compresses, and prepares the project for deployment to HostPinnacle

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set the archive name and other variables
DATE=$(date +%Y%m%d)
ARCHIVE_NAME="barberian_${DATE}_hostpinnacle.tar.gz"
MANIFEST_NAME="barberian_manifest_${DATE}.txt"
README_NAME="HOSTPINNACLE_README.md"
DEPLOYMENT_DIR="hostpinnacle_deployment"

echo -e "${YELLOW}=== Barberian Deployment to HostPinnacle ===${NC}"
echo -e "${YELLOW}=== $(date) ===${NC}"
echo ""

# Step 1: Clean up previous deployment files
echo -e "${YELLOW}Step 1: Cleaning up previous deployment files...${NC}"
if [ -d "$DEPLOYMENT_DIR" ]; then
    rm -rf "$DEPLOYMENT_DIR"
    echo -e "${GREEN}Previous deployment directory removed.${NC}"
fi
mkdir -p "$DEPLOYMENT_DIR"
echo -e "${GREEN}Created new deployment directory: $DEPLOYMENT_DIR${NC}"
echo ""

# Step 2: Run tests
echo -e "${YELLOW}Step 2: Running tests...${NC}"
python manage.py test
if [ $? -ne 0 ]; then
    echo -e "${RED}Tests failed. Aborting deployment.${NC}"
    exit 1
fi
echo -e "${GREEN}All tests passed.${NC}"
echo ""

# Step 3: Collect static files
echo -e "${YELLOW}Step 3: Collecting static files...${NC}"
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo -e "${RED}Static file collection failed. Aborting deployment.${NC}"
    exit 1
fi
echo -e "${GREEN}Static files collected successfully.${NC}"
echo ""

# Step 4: Create a manifest of files to be included
echo -e "${YELLOW}Step 4: Creating manifest of files...${NC}"
find . -type f \
    -not -path "./venv/*" \
    -not -path "./env/*" \
    -not -path "./.git/*" \
    -not -path "*/__pycache__/*" \
    -not -name "*.pyc" \
    -not -name "*.pyo" \
    -not -name "*.pyd" \
    -not -name "db.sqlite3" \
    -not -path "./media/*" \
    -not -path "./staticfiles/*" \
    -not -name ".env" \
    -not -path "./brber-master/*" \
    -not -path "./$DEPLOYMENT_DIR/*" \
    | sort > "$DEPLOYMENT_DIR/$MANIFEST_NAME"

# Count the number of files
FILE_COUNT=$(wc -l < "$DEPLOYMENT_DIR/$MANIFEST_NAME")
echo -e "${GREEN}Found $FILE_COUNT files to include in the archive.${NC}"
echo ""

# Step 5: Create deployment README
echo -e "${YELLOW}Step 5: Creating deployment README...${NC}"
cat > "$DEPLOYMENT_DIR/$README_NAME" << 'EOF'
# Barberian Deployment to HostPinnacle

This package contains the Barberian Barbershop Management System, ready for deployment to HostPinnacle.

## Deployment Steps

### 1. Create a HostPinnacle Account

If you don't already have a HostPinnacle account, sign up at https://hostpinnacle.com/

### 2. Create a New Application

1. Log in to your HostPinnacle dashboard
2. Click "Create New App"
3. Choose a name for your application (e.g., "barberian")
4. Select the region closest to your target audience
5. Click "Create App"

### 3. Set Up PostgreSQL Database

1. Go to the "Resources" tab
2. Add a PostgreSQL database add-on
3. Choose a plan that fits your needs
4. Note the database credentials provided

### 4. Configure Environment Variables

1. Go to the "Settings" tab
2. Click "Reveal Config Vars"
3. Add the following environment variables:
   - `DEBUG`: Set to `False`
   - `SECRET_KEY`: Use a secure random key
   - `ALLOWED_HOSTS`: Add your app's domain
   - Database settings (from the database add-on):
     - `DB_ENGINE`: `django.db.backends.postgresql`
     - `DB_NAME`: Your database name
     - `DB_USER`: Your database user
     - `DB_PASSWORD`: Your database password
     - `DB_HOST`: Your database host
     - `DB_PORT`: Your database port (usually `5432`)
   - Email settings:
     - `EMAIL_BACKEND`: `django.core.mail.backends.smtp.EmailBackend`
     - `EMAIL_HOST`: Your SMTP server
     - `EMAIL_PORT`: Your SMTP port (usually `587`)
     - `EMAIL_USE_TLS`: `True`
     - `EMAIL_HOST_USER`: Your email address
     - `EMAIL_HOST_PASSWORD`: Your email password
   - Stripe settings (if applicable):
     - `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
     - `STRIPE_SECRET_KEY`: Your Stripe secret key

### 5. Deploy the Application

1. Go to the "Deploy" tab
2. Connect your GitHub repository or upload this archive
3. Choose the branch you want to deploy (usually `main` or `master`)
4. Click "Deploy Branch"

### 6. Run Migrations

After deployment, run migrations to set up your database:

1. Go to the "More" dropdown menu
2. Select "Run Console"
3. Run the following command:
   ```
   python manage.py migrate
   ```

### 7. Create a Superuser

Create an admin user to access the Django admin panel:

1. Go to the "More" dropdown menu
2. Select "Run Console"
3. Run the following command:
   ```
   python manage.py createsuperuser
   ```
4. Follow the prompts to create a superuser

### 8. Verify Deployment

1. Click "Open App" to view your deployed application
2. Navigate to `/admin/` to access the Django admin panel
3. Log in with the superuser credentials you created

## Troubleshooting

If you encounter any issues during deployment, check the logs:

1. Go to the "More" dropdown menu
2. Select "View Logs"
3. Look for error messages that might help identify the problem

Common issues:
- Missing environment variables
- Database connection problems
- Static files not being served correctly

## Support

For support or questions, please contact the development team or refer to the project documentation.
EOF
echo -e "${GREEN}Deployment README created.${NC}"
echo ""

# Step 6: Create the archive
echo -e "${YELLOW}Step 6: Creating archive...${NC}"
tar --exclude="venv" \
    --exclude="env" \
    --exclude=".git" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="*.pyo" \
    --exclude="*.pyd" \
    --exclude="db.sqlite3" \
    --exclude="media/*" \
    --exclude="staticfiles" \
    --exclude=".env" \
    --exclude="brber-master" \
    --exclude="barberian_*.tar.gz" \
    --exclude="$DEPLOYMENT_DIR" \
    -czvf "$DEPLOYMENT_DIR/$ARCHIVE_NAME" .

# Add the manifest to the archive
tar -rf "$DEPLOYMENT_DIR/$ARCHIVE_NAME" "$DEPLOYMENT_DIR/$MANIFEST_NAME" "$DEPLOYMENT_DIR/$README_NAME"

echo -e "${GREEN}Archive created: $DEPLOYMENT_DIR/$ARCHIVE_NAME${NC}"
echo -e "${GREEN}Size: $(du -h "$DEPLOYMENT_DIR/$ARCHIVE_NAME" | cut -f1)${NC}"
echo ""

# Step 7: Create a checksum file
echo -e "${YELLOW}Step 7: Creating checksum file...${NC}"
cd "$DEPLOYMENT_DIR"
md5sum "$ARCHIVE_NAME" > "${ARCHIVE_NAME}.md5"
cd ..
echo -e "${GREEN}Checksum file created: $DEPLOYMENT_DIR/${ARCHIVE_NAME}.md5${NC}"
echo ""

# Step 8: Create HostPinnacle-specific files
echo -e "${YELLOW}Step 8: Creating HostPinnacle-specific files...${NC}"

# Create a Procfile if it doesn't exist
if [ ! -f "Procfile" ]; then
    echo "web: gunicorn barberian.wsgi --log-file -" > "$DEPLOYMENT_DIR/Procfile"
    echo -e "${GREEN}Procfile created.${NC}"
else
    cp Procfile "$DEPLOYMENT_DIR/Procfile"
    echo -e "${GREEN}Existing Procfile copied.${NC}"
fi

# Create a runtime.txt file
python_version=$(python --version | cut -d' ' -f2)
echo "python-$python_version" > "$DEPLOYMENT_DIR/runtime.txt"
echo -e "${GREEN}runtime.txt created with Python version $python_version.${NC}"

# Copy requirements.txt
cp requirements.txt "$DEPLOYMENT_DIR/requirements.txt"
echo -e "${GREEN}requirements.txt copied.${NC}"

# Copy .env.example
cp .env.example "$DEPLOYMENT_DIR/.env.example"
echo -e "${GREEN}.env.example copied.${NC}"
echo ""

# Step 9: Create a deployment package
echo -e "${YELLOW}Step 9: Creating final deployment package...${NC}"
cd "$DEPLOYMENT_DIR"
zip -r "barberian_hostpinnacle_deployment_${DATE}.zip" *
cd ..
echo -e "${GREEN}Final deployment package created: $DEPLOYMENT_DIR/barberian_hostpinnacle_deployment_${DATE}.zip${NC}"
echo -e "${GREEN}Size: $(du -h "$DEPLOYMENT_DIR/barberian_hostpinnacle_deployment_${DATE}.zip" | cut -f1)${NC}"
echo ""

echo -e "${YELLOW}=== Deployment preparation complete ===${NC}"
echo -e "${YELLOW}The deployment package is ready in the '$DEPLOYMENT_DIR' directory.${NC}"
echo -e "${YELLOW}Follow the instructions in '$README_NAME' to deploy to HostPinnacle.${NC}"
echo ""

# List the deployment directory contents
echo -e "${YELLOW}Deployment directory contents:${NC}"
ls -la "$DEPLOYMENT_DIR"
