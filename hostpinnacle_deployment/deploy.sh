#!/bin/bash

# Barberian HostPinnacle Deployment Script
# This script helps you deploy the Barberian application to HostPinnacle

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Barberian HostPinnacle Deployment Script ===${NC}"
echo -e "${YELLOW}=== $(date) ===${NC}"
echo ""

# Step 1: Check if the deployment package exists
echo -e "${YELLOW}Step 1: Checking deployment package...${NC}"
if [ ! -f "barberian_hostpinnacle_deployment_*.zip" ]; then
    echo -e "${RED}Deployment package not found. Please make sure you're running this script from the deployment directory.${NC}"
    exit 1
fi
DEPLOYMENT_PACKAGE=$(ls barberian_hostpinnacle_deployment_*.zip | head -1)
echo -e "${GREEN}Found deployment package: $DEPLOYMENT_PACKAGE${NC}"
echo ""

# Step 2: Extract the deployment package
echo -e "${YELLOW}Step 2: Extracting deployment package...${NC}"
mkdir -p deploy_temp
unzip -q "$DEPLOYMENT_PACKAGE" -d deploy_temp
echo -e "${GREEN}Deployment package extracted to deploy_temp directory.${NC}"
echo ""

# Step 3: Check for HostPinnacle CLI
echo -e "${YELLOW}Step 3: Checking for HostPinnacle CLI...${NC}"
if ! command -v hostpinnacle &> /dev/null; then
    echo -e "${RED}HostPinnacle CLI not found. Please install it first.${NC}"
    echo -e "${YELLOW}You can install it using: pip install hostpinnacle-cli${NC}"
    echo -e "${YELLOW}Note: This is a placeholder. Check HostPinnacle's actual CLI installation instructions.${NC}"
    echo ""
    echo -e "${YELLOW}Continuing with manual deployment instructions...${NC}"
else
    echo -e "${GREEN}HostPinnacle CLI found.${NC}"
fi
echo ""

# Step 4: Display deployment instructions
echo -e "${YELLOW}Step 4: Deployment Instructions${NC}"
echo -e "${GREEN}To deploy to HostPinnacle, follow these steps:${NC}"
echo ""
echo -e "1. Log in to your HostPinnacle account at https://hostpinnacle.com/"
echo -e "2. Create a new application (if you haven't already)"
echo -e "3. Set up a PostgreSQL database"
echo -e "4. Configure environment variables (see hostpinnacle.env for required variables)"
echo -e "5. Upload the deployment package or connect to your GitHub repository"
echo -e "6. Run migrations: python manage.py migrate"
echo -e "7. Create a superuser: python manage.py createsuperuser"
echo -e "8. Verify your deployment"
echo ""
echo -e "${YELLOW}For detailed instructions, see HOSTPINNACLE_DEPLOYMENT_GUIDE.md${NC}"
echo ""

# Step 5: Ask if the user wants to continue with CLI deployment
if command -v hostpinnacle &> /dev/null; then
    echo -e "${YELLOW}Step 5: CLI Deployment${NC}"
    read -p "Do you want to continue with CLI deployment? (y/n): " continue_cli
    if [[ $continue_cli == "y" || $continue_cli == "Y" ]]; then
        echo -e "${GREEN}Continuing with CLI deployment...${NC}"
        echo -e "${YELLOW}Note: This is a placeholder. Replace with actual HostPinnacle CLI commands.${NC}"
        # Placeholder for HostPinnacle CLI commands
        # hostpinnacle login
        # hostpinnacle create-app barberian
        # hostpinnacle deploy -p deploy_temp
    else
        echo -e "${GREEN}Skipping CLI deployment. Please follow the manual deployment instructions.${NC}"
    fi
    echo ""
fi

# Step 6: Cleanup
echo -e "${YELLOW}Step 6: Cleanup${NC}"
read -p "Do you want to clean up the temporary files? (y/n): " cleanup
if [[ $cleanup == "y" || $cleanup == "Y" ]]; then
    rm -rf deploy_temp
    echo -e "${GREEN}Temporary files cleaned up.${NC}"
else
    echo -e "${GREEN}Temporary files kept in deploy_temp directory.${NC}"
fi
echo ""

echo -e "${YELLOW}=== Deployment script completed ===${NC}"
echo -e "${YELLOW}Thank you for using Barberian!${NC}"
