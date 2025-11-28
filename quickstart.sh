#!/bin/bash
#
# Cradle Quickstart Configuration Script
# Customize your project name, colors, and pages
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
DEFAULT_NAME="Cradle"
DEFAULT_DESCRIPTION="Enterprise Multi-Platform Architecture"
DEFAULT_PRIMARY_COLOR="blue"
DEFAULT_PAGES="dashboard,settings,projects"

# Configuration file
CONFIG_FILE=".quickstart.json"

print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║   🚀 Enterprise Platform Quickstart Configuration 🚀     ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "\n${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Prompt with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local result

    echo -en "${CYAN}$prompt ${NC}[${default}]: "
    read result
    echo "${result:-$default}"
}

# Prompt for selection
prompt_select() {
    local prompt="$1"
    shift
    local options=("$@")
    local i=1

    echo -e "${CYAN}$prompt${NC}"
    for opt in "${options[@]}"; do
        echo "  $i) $opt"
        ((i++))
    done

    echo -en "Select [1]: "
    read selection
    selection=${selection:-1}

    if [[ $selection -ge 1 && $selection -le ${#options[@]} ]]; then
        echo "${options[$((selection-1))]}"
    else
        echo "${options[0]}"
    fi
}

# Convert string to lowercase
to_lower() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

# Convert string to snake_case
to_snake_case() {
    echo "$1" | sed 's/[^a-zA-Z0-9]/_/g' | tr '[:upper:]' '[:lower:]'
}

# Convert string to kebab-case
to_kebab_case() {
    echo "$1" | sed 's/[^a-zA-Z0-9]/-/g' | tr '[:upper:]' '[:lower:]'
}

# Get Tailwind color classes
get_color_classes() {
    local color="$1"
    case "$color" in
        blue)
            echo "blue-600 blue-700 blue-500 blue-50 blue-100 blue-800 blue-900 blue-200 blue-300 blue-400"
            ;;
        indigo)
            echo "indigo-600 indigo-700 indigo-500 indigo-50 indigo-100 indigo-800 indigo-900 indigo-200 indigo-300 indigo-400"
            ;;
        purple)
            echo "purple-600 purple-700 purple-500 purple-50 purple-100 purple-800 purple-900 purple-200 purple-300 purple-400"
            ;;
        pink)
            echo "pink-600 pink-700 pink-500 pink-50 pink-100 pink-800 pink-900 pink-200 pink-300 pink-400"
            ;;
        red)
            echo "red-600 red-700 red-500 red-50 red-100 red-800 red-900 red-200 red-300 red-400"
            ;;
        orange)
            echo "orange-600 orange-700 orange-500 orange-50 orange-100 orange-800 orange-900 orange-200 orange-300 orange-400"
            ;;
        green)
            echo "green-600 green-700 green-500 green-50 green-100 green-800 green-900 green-200 green-300 green-400"
            ;;
        teal)
            echo "teal-600 teal-700 teal-500 teal-50 teal-100 teal-800 teal-900 teal-200 teal-300 teal-400"
            ;;
        cyan)
            echo "cyan-600 cyan-700 cyan-500 cyan-50 cyan-100 cyan-800 cyan-900 cyan-200 cyan-300 cyan-400"
            ;;
        gray)
            echo "gray-600 gray-700 gray-500 gray-50 gray-100 gray-800 gray-900 gray-200 gray-300 gray-400"
            ;;
        *)
            echo "blue-600 blue-700 blue-500 blue-50 blue-100 blue-800 blue-900 blue-200 blue-300 blue-400"
            ;;
    esac
}

# Main configuration
main() {
    print_banner

    echo -e "This script will configure your project with custom settings.\n"

    # Step 1: Project Name
    print_step "Step 1: Project Name"
    PROJECT_NAME=$(prompt_with_default "Enter your project name" "$DEFAULT_NAME")
    PROJECT_NAME_LOWER=$(to_lower "$PROJECT_NAME")
    PROJECT_NAME_SNAKE=$(to_snake_case "$PROJECT_NAME")
    PROJECT_NAME_KEBAB=$(to_kebab_case "$PROJECT_NAME")

    # Step 2: Description
    print_step "Step 2: Project Description"
    PROJECT_DESC=$(prompt_with_default "Enter a short description" "$DEFAULT_DESCRIPTION")

    # Step 3: Color Scheme
    print_step "Step 3: Color Scheme"
    PRIMARY_COLOR=$(prompt_select "Choose your primary color:" \
        "blue" "indigo" "purple" "pink" "red" "orange" "green" "teal" "cyan" "gray")

    # Step 4: Pages
    print_step "Step 4: Dashboard Pages"
    echo -e "Enter comma-separated page names (e.g., dashboard,settings,projects,analytics)"
    PAGES_INPUT=$(prompt_with_default "Pages to create" "$DEFAULT_PAGES")
    IFS=',' read -ra PAGES <<< "$PAGES_INPUT"

    # Step 5: Features
    print_step "Step 5: Optional Features"
    echo -en "${CYAN}Enable AI Disclosure banner? ${NC}[Y/n]: "
    read AI_DISCLOSURE
    AI_DISCLOSURE=${AI_DISCLOSURE:-Y}

    echo -en "${CYAN}Enable dark mode support? ${NC}[Y/n]: "
    read DARK_MODE
    DARK_MODE=${DARK_MODE:-Y}

    # Confirmation
    echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Configuration Summary:${NC}"
    echo -e "  Project Name:  ${GREEN}$PROJECT_NAME${NC}"
    echo -e "  Description:   ${GREEN}$PROJECT_DESC${NC}"
    echo -e "  Primary Color: ${GREEN}$PRIMARY_COLOR${NC}"
    echo -e "  Pages:         ${GREEN}${PAGES[*]}${NC}"
    echo -e "  AI Disclosure: ${GREEN}$AI_DISCLOSURE${NC}"
    echo -e "  Dark Mode:     ${GREEN}$DARK_MODE${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    echo -en "\n${CYAN}Proceed with configuration? ${NC}[Y/n]: "
    read CONFIRM
    CONFIRM=${CONFIRM:-Y}

    if [[ ! "$CONFIRM" =~ ^[Yy] ]]; then
        print_warning "Configuration cancelled."
        exit 0
    fi

    # Apply configuration
    echo -e "\n${BLUE}Applying configuration...${NC}\n"

    apply_configuration

    echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✓ Configuration complete!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "\nNext steps:"
    echo -e "  1. ${CYAN}docker compose up${NC} - Start all services"
    echo -e "  2. Open ${CYAN}http://localhost:3010${NC} - View your app"
    echo -e "  3. Login with ${CYAN}admin@example.com / password${NC}"
    echo -e "\nHappy building! 🚀\n"
}

apply_configuration() {
    # Save configuration
    save_config

    # Update backend
    update_backend_config

    # Update frontend
    update_frontend_config

    # Create pages
    create_pages

    # Update docker-compose
    update_docker_compose

    # Update README
    update_readme
}

save_config() {
    print_step "Saving configuration..."

    cat > "$CONFIG_FILE" << EOF
{
    "projectName": "$PROJECT_NAME",
    "projectNameLower": "$PROJECT_NAME_LOWER",
    "projectNameSnake": "$PROJECT_NAME_SNAKE",
    "projectNameKebab": "$PROJECT_NAME_KEBAB",
    "description": "$PROJECT_DESC",
    "primaryColor": "$PRIMARY_COLOR",
    "pages": [$(printf '"%s",' "${PAGES[@]}" | sed 's/,$//')]
    "features": {
        "aiDisclosure": $([ "$AI_DISCLOSURE" =~ ^[Yy] ] && echo "true" || echo "false"),
        "darkMode": $([ "$DARK_MODE" =~ ^[Yy] ] && echo "true" || echo "false")
    }
}
EOF

    print_success "Configuration saved to $CONFIG_FILE"
}

update_backend_config() {
    print_step "Updating backend configuration..."

    # Update app name in config.py
    sed -i.bak "s/app_name: str = \"Cradle\"/app_name: str = \"$PROJECT_NAME\"/" backend/app/config.py
    sed -i.bak "s/title=settings.app_name/title=\"$PROJECT_NAME\"/" backend/app/main.py
    sed -i.bak "s/description=\"Cradle API - Enterprise Multi-Platform Architecture\"/description=\"$PROJECT_NAME API - $PROJECT_DESC\"/" backend/app/main.py

    # Update secret names
    sed -i.bak "s/cradle\//$PROJECT_NAME_LOWER\//g" backend/app/abstractions/secret_vault.py 2>/dev/null || true

    # Clean up backup files
    find backend -name "*.bak" -delete 2>/dev/null || true

    print_success "Backend configuration updated"
}

update_frontend_config() {
    print_step "Updating frontend configuration..."

    # Update package.json name
    sed -i.bak "s/\"name\": \"cradle-frontend\"/\"name\": \"$PROJECT_NAME_KEBAB-frontend\"/" frontend/package.json

    # Update layout.tsx title
    sed -i.bak "s/title: 'Cradle'/title: '$PROJECT_NAME'/" frontend/src/app/layout.tsx
    sed -i.bak "s/description: 'Enterprise Multi-Platform Architecture'/description: '$PROJECT_DESC'/" frontend/src/app/layout.tsx

    # Update auth.ts token keys
    sed -i.bak "s/cradle_access_token/${PROJECT_NAME_SNAKE}_access_token/g" frontend/src/lib/auth.ts
    sed -i.bak "s/cradle_refresh_token/${PROJECT_NAME_SNAKE}_refresh_token/g" frontend/src/lib/auth.ts

    # Update color scheme in components
    update_color_scheme

    # Update header in dashboard layout
    sed -i.bak "s/>Cradle</>$PROJECT_NAME</" frontend/src/app/\(dashboard\)/layout.tsx

    # Update login page
    sed -i.bak "s/>Cradle</>$PROJECT_NAME</" frontend/src/app/\(auth\)/login/page.tsx

    # Update home page
    sed -i.bak "s/>Cradle</>$PROJECT_NAME</" frontend/src/app/page.tsx

    # Clean up backup files
    find frontend -name "*.bak" -delete 2>/dev/null || true

    print_success "Frontend configuration updated"
}

update_color_scheme() {
    local old_color="blue"
    local new_color="$PRIMARY_COLOR"

    if [ "$old_color" != "$new_color" ]; then
        # Update all frontend files with new color
        find frontend/src -name "*.tsx" -exec sed -i.bak \
            -e "s/bg-blue-/bg-$new_color-/g" \
            -e "s/text-blue-/text-$new_color-/g" \
            -e "s/border-blue-/border-$new_color-/g" \
            -e "s/hover:bg-blue-/hover:bg-$new_color-/g" \
            -e "s/hover:text-blue-/hover:text-$new_color-/g" \
            -e "s/focus:ring-blue-/focus:ring-$new_color-/g" \
            -e "s/focus:border-blue-/focus:border-$new_color-/g" \
            -e "s/ring-blue-/ring-$new_color-/g" \
            {} \;

        print_success "Color scheme updated to $new_color"
    fi
}

create_pages() {
    print_step "Creating dashboard pages..."

    for page in "${PAGES[@]}"; do
        page=$(echo "$page" | xargs)  # Trim whitespace
        page_lower=$(to_lower "$page")
        page_title=$(echo "$page" | sed 's/.*/\u&/')  # Capitalize first letter

        # Skip if dashboard (already exists)
        if [ "$page_lower" == "dashboard" ]; then
            continue
        fi

        # Create page directory and file
        mkdir -p "frontend/src/app/(dashboard)/$page_lower"

        cat > "frontend/src/app/(dashboard)/$page_lower/page.tsx" << EOF
'use client';

import { useState } from 'react';

export default function ${page_title}Page() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          ${page_title}
        </h2>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <p className="text-gray-600 dark:text-gray-400">
          ${page_title} page content goes here.
        </p>
      </div>
    </div>
  );
}
EOF

        print_success "Created page: $page_lower"
    done

    # Update navigation in dashboard layout
    update_navigation
}

update_navigation() {
    print_step "Updating navigation..."

    # Generate navigation items
    local nav_items=""
    for page in "${PAGES[@]}"; do
        page=$(echo "$page" | xargs)
        page_lower=$(to_lower "$page")
        page_title=$(echo "$page" | sed 's/.*/\u&/')
        nav_items="$nav_items
            <a
              href=\"/$page_lower\"
              className=\"px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white rounded-md hover:bg-gray-100 dark:hover:bg-gray-700\"
            >
              $page_title
            </a>"
    done

    # Create updated layout with navigation
    cat > "frontend/src/app/(dashboard)/layout.tsx" << EOF
'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { getAccessToken, isTokenExpired, clearTokens, decodeToken, refreshAccessToken } from '@/lib/auth';
import type { TokenPayload } from '@/types';
import { AIDisclosureBanner } from '@/components/AIDisclosureBanner';

const navigation = [
$(for page in "${PAGES[@]}"; do
    page=$(echo "$page" | xargs)
    page_lower=$(to_lower "$page")
    page_title=$(echo "$page" | sed 's/.*/\u&/')
    echo "  { name: '$page_title', href: '/$page_lower' },"
done)
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<TokenPayload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = getAccessToken();

      if (!token) {
        router.push('/login');
        return;
      }

      if (isTokenExpired(token)) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          router.push('/login');
          return;
        }
        const newToken = getAccessToken();
        if (newToken) {
          setUser(decodeToken(newToken));
        }
      } else {
        setUser(decodeToken(token));
      }

      setLoading(false);
    };

    checkAuth();
  }, [router]);

  const handleLogout = () => {
    clearTokens();
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                $PROJECT_NAME
              </h1>
              <nav className="hidden md:flex space-x-1">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={\`px-3 py-2 text-sm font-medium rounded-md transition-colors \${
                      pathname === item.href || pathname.startsWith(item.href + '/')
                        ? 'text-${PRIMARY_COLOR}-600 bg-${PRIMARY_COLOR}-50 dark:text-${PRIMARY_COLOR}-400 dark:bg-${PRIMARY_COLOR}-900/20'
                        : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                    }\`}
                  >
                    {item.name}
                  </Link>
                ))}
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {user?.email}
              </span>
              {user?.roles?.includes('admin') && (
                <span className="px-2 py-1 text-xs bg-${PRIMARY_COLOR}-100 text-${PRIMARY_COLOR}-800 dark:bg-${PRIMARY_COLOR}-900 dark:text-${PRIMARY_COLOR}-200 rounded">
                  Admin
                </span>
              )}
              <button
                onClick={handleLogout}
                className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* AI Disclosure Banner */}
      <AIDisclosureBanner />
    </div>
  );
}
EOF

    print_success "Navigation updated"
}

update_docker_compose() {
    print_step "Updating Docker Compose..."

    # Update service names and container names
    sed -i.bak "s/cradle-uploads/${PROJECT_NAME_LOWER}-uploads/g" docker-compose.yml
    sed -i.bak "s/cradle-exports/${PROJECT_NAME_LOWER}-exports/g" docker-compose.yml
    sed -i.bak "s/POSTGRES_DB: cradle/POSTGRES_DB: $PROJECT_NAME_LOWER/" docker-compose.yml

    # Update config files
    sed -i.bak "s/cradle-uploads/${PROJECT_NAME_LOWER}-uploads/g" config/profile.dev.yaml
    sed -i.bak "s/cradle-exports/${PROJECT_NAME_LOWER}-exports/g" config/profile.dev.yaml
    sed -i.bak "s/cradle-uploads/${PROJECT_NAME_LOWER}-uploads/g" config/profile.prod.yaml
    sed -i.bak "s/cradle-exports/${PROJECT_NAME_LOWER}-exports/g" config/profile.prod.yaml

    # Update LocalStack init
    sed -i.bak "s/cradle-uploads/${PROJECT_NAME_LOWER}-uploads/g" infra/localstack/init-aws.sh
    sed -i.bak "s/cradle-exports/${PROJECT_NAME_LOWER}-exports/g" infra/localstack/init-aws.sh
    sed -i.bak "s/cradle\//${PROJECT_NAME_LOWER}\//g" infra/localstack/init-aws.sh

    # Clean up backup files
    find . -maxdepth 1 -name "*.bak" -delete 2>/dev/null || true
    find config -name "*.bak" -delete 2>/dev/null || true
    find infra -name "*.bak" -delete 2>/dev/null || true

    print_success "Docker Compose updated"
}

update_readme() {
    print_step "Updating README..."

    cat > README.md << EOF
# $PROJECT_NAME

$PROJECT_DESC

## Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 14 (TypeScript)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **AWS Emulation**: LocalStack (S3, Secrets Manager)
- **Containerization**: Docker Compose

## Quick Start

\`\`\`bash
# Start all services
docker compose up

# Or run in background
make up
\`\`\`

Once running:
- **Frontend**: http://localhost:3010
- **Backend API**: http://localhost:8010
- **API Docs**: http://localhost:8010/docs

### Default Credentials

\`\`\`
Email: admin@example.com
Password: password
\`\`\`

## Available Pages

$(for page in "${PAGES[@]}"; do
    page=$(echo "$page" | xargs)
    page_lower=$(to_lower "$page")
    page_title=$(echo "$page" | sed 's/.*/\u&/')
    echo "- **$page_title**: /$page_lower"
done)

## Common Commands

\`\`\`bash
make up              # Start services (background)
make down            # Stop services
make logs            # View logs
make shell-backend   # Backend shell
make shell-frontend  # Frontend shell
make test            # Run tests
make reset           # Reset everything
\`\`\`

## Project Structure

\`\`\`
$PROJECT_NAME_LOWER/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── abstractions/ # SecretVault, BlobStore, AuditLogger
│   │   ├── core/         # Middleware, security, context
│   │   ├── models/       # SQLAlchemy models
│   │   └── schemas/      # Pydantic schemas
│   └── tests/
│
├── frontend/              # Next.js application
│   └── src/
│       ├── app/          # App Router pages
│       ├── components/   # React components
│       └── lib/          # API client, utilities
│
├── config/                # Profile-based configuration
└── infra/                 # Infrastructure setup
\`\`\`

## Configuration

This project was configured with:
- **Primary Color**: $PRIMARY_COLOR
- **Pages**: ${PAGES[*]}

To reconfigure, run \`./quickstart.sh\` again.

## License

MIT
EOF

    print_success "README updated"
}

# Run main function
main "$@"
