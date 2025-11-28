#!/usr/bin/env python3
"""
Quickstart Configuration Script

Reads configuration from quickstart.config.json and applies changes to the project.
Can also run interactively to gather configuration.

Usage:
    python scripts/configure.py              # Interactive mode
    python scripts/configure.py --from-file  # Apply from quickstart.config.json
    python scripts/configure.py --reset      # Reset to defaults
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def print_banner():
    print(f"{Colors.CYAN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║   🚀 Enterprise Platform Quickstart Configuration 🚀     ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.NC}")


def print_step(msg: str):
    print(f"\n{Colors.BLUE}▶ {msg}{Colors.NC}")


def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.NC}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.NC}")


def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.NC}")


# Available color schemes
COLOR_SCHEMES = [
    "blue", "indigo", "purple", "pink", "red",
    "orange", "green", "teal", "cyan", "gray"
]

# Page icons (for future use)
PAGE_ICONS = {
    "dashboard": "home",
    "settings": "cog",
    "projects": "folder",
    "analytics": "chart-bar",
    "users": "users",
    "reports": "document",
    "integrations": "puzzle",
    "billing": "credit-card",
}


def to_snake_case(s: str) -> str:
    """Convert string to snake_case."""
    s = re.sub(r'[^a-zA-Z0-9]', '_', s)
    return s.lower()


def to_kebab_case(s: str) -> str:
    """Convert string to kebab-case."""
    s = re.sub(r'[^a-zA-Z0-9]', '-', s)
    return s.lower()


def to_title_case(s: str) -> str:
    """Convert string to Title Case."""
    return s.replace('_', ' ').replace('-', ' ').title()


def prompt(msg: str, default: str = "") -> str:
    """Prompt user for input with optional default."""
    if default:
        result = input(f"{Colors.CYAN}{msg} {Colors.NC}[{default}]: ").strip()
        return result if result else default
    return input(f"{Colors.CYAN}{msg}: {Colors.NC}").strip()


def prompt_select(msg: str, options: list[str], default: int = 0) -> str:
    """Prompt user to select from options."""
    print(f"{Colors.CYAN}{msg}{Colors.NC}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}) {opt}")

    selection = input(f"Select [{default + 1}]: ").strip()
    try:
        idx = int(selection) - 1 if selection else default
        if 0 <= idx < len(options):
            return options[idx]
    except ValueError:
        pass
    return options[default]


def prompt_yes_no(msg: str, default: bool = True) -> bool:
    """Prompt for yes/no answer."""
    default_str = "Y/n" if default else "y/N"
    result = input(f"{Colors.CYAN}{msg} {Colors.NC}[{default_str}]: ").strip().lower()
    if not result:
        return default
    return result in ('y', 'yes', 'true', '1')


def gather_config_interactive() -> dict[str, Any]:
    """Gather configuration interactively."""
    print_banner()
    print("This script will configure your project with custom settings.\n")

    config = {}

    # Project name
    print_step("Step 1: Project Name")
    config['projectName'] = prompt("Enter your project name", "Cradle")

    # Description
    print_step("Step 2: Project Description")
    config['description'] = prompt(
        "Enter a short description",
        "Enterprise Multi-Platform Architecture"
    )

    # Color scheme
    print_step("Step 3: Color Scheme")
    config['primaryColor'] = prompt_select(
        "Choose your primary color:",
        COLOR_SCHEMES,
        default=0
    )

    # Pages
    print_step("Step 4: Dashboard Pages")
    print("Enter comma-separated page names (e.g., dashboard,settings,projects)")
    pages_input = prompt("Pages to create", "dashboard,settings")
    page_names = [p.strip() for p in pages_input.split(',') if p.strip()]

    config['pages'] = []
    for name in page_names:
        config['pages'].append({
            'name': to_title_case(name),
            'path': to_kebab_case(name),
            'icon': PAGE_ICONS.get(name.lower(), 'circle'),
            'description': f'{to_title_case(name)} page'
        })

    # Features
    print_step("Step 5: Optional Features")
    config['features'] = {
        'aiDisclosure': prompt_yes_no("Enable AI Disclosure banner?", True),
        'darkMode': prompt_yes_no("Enable dark mode support?", True),
        'multiTenant': prompt_yes_no("Enable multi-tenant support?", True),
    }

    # Auth defaults
    config['auth'] = {
        'defaultEmail': 'admin@example.com',
        'defaultPassword': 'password'
    }

    config['branding'] = {
        'logoText': None,
        'tagline': None
    }

    return config


def load_config_from_file(path: str = "quickstart.config.json") -> dict[str, Any]:
    """Load configuration from JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_config(config: dict[str, Any], path: str = "quickstart.config.json"):
    """Save configuration to JSON file."""
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)
    print_success(f"Configuration saved to {path}")


def replace_in_file(filepath: str, replacements: dict[str, str]):
    """Replace multiple strings in a file."""
    path = Path(filepath)
    if not path.exists():
        print_warning(f"File not found: {filepath}")
        return

    content = path.read_text()
    for old, new in replacements.items():
        content = content.replace(old, new)
    path.write_text(content)


def replace_color_in_file(filepath: str, old_color: str, new_color: str):
    """Replace Tailwind color classes in a file."""
    path = Path(filepath)
    if not path.exists():
        return

    content = path.read_text()

    # Replace various color usages
    patterns = [
        (f'bg-{old_color}-', f'bg-{new_color}-'),
        (f'text-{old_color}-', f'text-{new_color}-'),
        (f'border-{old_color}-', f'border-{new_color}-'),
        (f'ring-{old_color}-', f'ring-{new_color}-'),
        (f'hover:bg-{old_color}-', f'hover:bg-{new_color}-'),
        (f'hover:text-{old_color}-', f'hover:text-{new_color}-'),
        (f'focus:ring-{old_color}-', f'focus:ring-{new_color}-'),
        (f'focus:border-{old_color}-', f'focus:border-{new_color}-'),
    ]

    for old, new in patterns:
        content = content.replace(old, new)

    path.write_text(content)


def apply_config(config: dict[str, Any]):
    """Apply configuration to the project."""
    project_name = config['projectName']
    project_lower = project_name.lower()
    project_snake = to_snake_case(project_name)
    project_kebab = to_kebab_case(project_name)
    description = config['description']
    primary_color = config['primaryColor']
    pages = config['pages']

    print_step("Applying configuration...")

    # Update backend
    update_backend(project_name, project_lower, project_snake, description)

    # Update frontend
    update_frontend(project_name, project_snake, description, primary_color)

    # Create pages
    create_pages(pages, project_name, primary_color)

    # Update infrastructure
    update_infrastructure(project_lower)

    # Update README
    update_readme(config)

    print_success("Configuration applied successfully!")


def update_backend(name: str, name_lower: str, name_snake: str, desc: str):
    """Update backend configuration."""
    print_step("Updating backend...")

    # config.py
    replace_in_file('backend/app/config.py', {
        'app_name: str = "Cradle"': f'app_name: str = "{name}"',
    })

    # main.py
    replace_in_file('backend/app/main.py', {
        'title="Cradle"': f'title="{name}"',
        'description="Cradle API - Enterprise Multi-Platform Architecture"':
            f'description="{name} API - {desc}"',
    })

    # S3 bucket names in config
    replace_in_file('backend/app/config.py', {
        's3_uploads_bucket: str = "cradle-uploads"':
            f's3_uploads_bucket: str = "{name_lower}-uploads"',
        's3_exports_bucket: str = "cradle-exports"':
            f's3_exports_bucket: str = "{name_lower}-exports"',
    })

    print_success("Backend updated")


def update_frontend(name: str, name_snake: str, desc: str, color: str):
    """Update frontend configuration."""
    print_step("Updating frontend...")

    # package.json
    replace_in_file('frontend/package.json', {
        '"name": "cradle-frontend"': f'"name": "{to_kebab_case(name)}-frontend"',
    })

    # layout.tsx (root)
    replace_in_file('frontend/src/app/layout.tsx', {
        "title: 'Cradle'": f"title: '{name}'",
        "description: 'Enterprise Multi-Platform Architecture'":
            f"description: '{desc}'",
    })

    # auth.ts (token keys)
    replace_in_file('frontend/src/lib/auth.ts', {
        'cradle_access_token': f'{name_snake}_access_token',
        'cradle_refresh_token': f'{name_snake}_refresh_token',
    })

    # Update project name in components
    for tsx_file in Path('frontend/src').rglob('*.tsx'):
        replace_in_file(str(tsx_file), {
            '>Cradle<': f'>{name}<',
        })

    # Update color scheme
    if color != 'blue':
        print_step(f"Updating color scheme to {color}...")
        for tsx_file in Path('frontend/src').rglob('*.tsx'):
            replace_color_in_file(str(tsx_file), 'blue', color)

    print_success("Frontend updated")


def create_pages(pages: list[dict], project_name: str, color: str):
    """Create dashboard pages."""
    print_step("Creating pages...")

    pages_dir = Path('frontend/src/app/(dashboard)')

    for page in pages:
        page_path = page['path']
        page_name = page['name']

        # Skip dashboard (already exists)
        if page_path == 'dashboard':
            continue

        # Create directory
        page_dir = pages_dir / page_path
        page_dir.mkdir(parents=True, exist_ok=True)

        # Create page file
        page_content = f'''\'use client\';

export default function {page_name.replace(' ', '')}Page() {{
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          {page_name}
        </h2>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <p className="text-gray-600 dark:text-gray-400">
          {page_name} page content goes here.
        </p>
      </div>
    </div>
  );
}}
'''
        (page_dir / 'page.tsx').write_text(page_content)
        print_success(f"Created page: {page_path}")

    # Update navigation in layout
    update_navigation(pages, project_name, color)


def update_navigation(pages: list[dict], project_name: str, color: str):
    """Update dashboard layout with navigation."""
    print_step("Updating navigation...")

    nav_items = ',\n'.join([
        f"  {{ name: '{p['name']}', href: '/{p['path']}' }}"
        for p in pages
    ])

    layout_content = f'''\'use client\';

import {{ useEffect, useState }} from 'react';
import {{ useRouter, usePathname }} from 'next/navigation';
import Link from 'next/link';
import {{ getAccessToken, isTokenExpired, clearTokens, decodeToken, refreshAccessToken }} from '@/lib/auth';
import type {{ TokenPayload }} from '@/types';
import {{ AIDisclosureBanner }} from '@/components/AIDisclosureBanner';

const navigation = [
{nav_items}
];

export default function DashboardLayout({{
  children,
}}: {{
  children: React.ReactNode;
}}) {{
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<TokenPayload | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {{
    const checkAuth = async () => {{
      const token = getAccessToken();

      if (!token) {{
        router.push('/login');
        return;
      }}

      if (isTokenExpired(token)) {{
        const refreshed = await refreshAccessToken();
        if (!refreshed) {{
          router.push('/login');
          return;
        }}
        const newToken = getAccessToken();
        if (newToken) {{
          setUser(decodeToken(newToken));
        }}
      }} else {{
        setUser(decodeToken(token));
      }}

      setLoading(false);
    }};

    checkAuth();
  }}, [router]);

  const handleLogout = () => {{
    clearTokens();
    router.push('/login');
  }};

  if (loading) {{
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }}

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {{/* Header */}}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                {project_name}
              </h1>
              <nav className="hidden md:flex space-x-1">
                {{navigation.map((item) => (
                  <Link
                    key={{item.name}}
                    href={{item.href}}
                    className={{`px-3 py-2 text-sm font-medium rounded-md transition-colors ${{
                      pathname === item.href || pathname.startsWith(item.href + '/')
                        ? 'text-{color}-600 bg-{color}-50 dark:text-{color}-400 dark:bg-{color}-900/20'
                        : 'text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                    }}`}}
                  >
                    {{item.name}}
                  </Link>
                ))}}
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {{user?.email}}
              </span>
              {{user?.roles?.includes('admin') && (
                <span className="px-2 py-1 text-xs bg-{color}-100 text-{color}-800 dark:bg-{color}-900 dark:text-{color}-200 rounded">
                  Admin
                </span>
              )}}
              <button
                onClick={{handleLogout}}
                className="text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {{/* Main content */}}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {{children}}
      </main>

      {{/* AI Disclosure Banner */}}
      <AIDisclosureBanner />
    </div>
  );
}}
'''

    layout_path = Path('frontend/src/app/(dashboard)/layout.tsx')
    layout_path.write_text(layout_content)
    print_success("Navigation updated")


def update_infrastructure(name_lower: str):
    """Update infrastructure configuration."""
    print_step("Updating infrastructure...")

    # docker-compose.yml
    replace_in_file('docker-compose.yml', {
        'cradle-uploads': f'{name_lower}-uploads',
        'cradle-exports': f'{name_lower}-exports',
        'POSTGRES_DB: cradle': f'POSTGRES_DB: {name_lower}',
    })

    # Profile configs
    for profile in ['dev', 'prod']:
        replace_in_file(f'config/profile.{profile}.yaml', {
            'cradle-uploads': f'{name_lower}-uploads',
            'cradle-exports': f'{name_lower}-exports',
        })

    # LocalStack init
    replace_in_file('infra/localstack/init-aws.sh', {
        'cradle-uploads': f'{name_lower}-uploads',
        'cradle-exports': f'{name_lower}-exports',
        'cradle/': f'{name_lower}/',
    })

    print_success("Infrastructure updated")


def update_readme(config: dict[str, Any]):
    """Update README with project info."""
    print_step("Updating README...")

    name = config['projectName']
    desc = config['description']
    pages = config['pages']
    color = config['primaryColor']

    pages_list = '\n'.join([
        f"- **{p['name']}**: /{p['path']}"
        for p in pages
    ])

    readme = f'''# {name}

{desc}

## Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Next.js 14 (TypeScript)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **AWS Emulation**: LocalStack (S3, Secrets Manager)
- **Containerization**: Docker Compose

## Quick Start

```bash
# Start all services
docker compose up

# Or run in background
make up
```

Once running:
- **Frontend**: http://localhost:3010
- **Backend API**: http://localhost:8010
- **API Docs**: http://localhost:8010/docs

### Default Credentials

```
Email: admin@example.com
Password: password
```

## Available Pages

{pages_list}

## Common Commands

```bash
make up              # Start services (background)
make down            # Stop services
make logs            # View logs
make shell-backend   # Backend shell
make shell-frontend  # Frontend shell
make test            # Run tests
make reset           # Reset everything
```

## Configuration

This project was configured with:
- **Primary Color**: {color}
- **Pages**: {', '.join(p['name'] for p in pages)}

To reconfigure, edit `quickstart.config.json` and run:
```bash
python scripts/configure.py --from-file
```

Or run interactively:
```bash
python scripts/configure.py
```

## License

MIT
'''

    Path('README.md').write_text(readme)
    print_success("README updated")


def print_summary(config: dict[str, Any]):
    """Print configuration summary."""
    print(f"\n{Colors.YELLOW}{'━' * 60}{Colors.NC}")
    print(f"{Colors.CYAN}Configuration Summary:{Colors.NC}")
    print(f"  Project Name:  {Colors.GREEN}{config['projectName']}{Colors.NC}")
    print(f"  Description:   {Colors.GREEN}{config['description']}{Colors.NC}")
    print(f"  Primary Color: {Colors.GREEN}{config['primaryColor']}{Colors.NC}")
    print(f"  Pages:         {Colors.GREEN}{', '.join(p['name'] for p in config['pages'])}{Colors.NC}")
    print(f"{Colors.YELLOW}{'━' * 60}{Colors.NC}")


def main():
    os.chdir(Path(__file__).parent.parent)  # Change to project root

    if '--from-file' in sys.argv:
        # Load from config file
        print_banner()
        config = load_config_from_file()
        print_summary(config)
        if prompt_yes_no("\nApply this configuration?", True):
            apply_config(config)
    elif '--reset' in sys.argv:
        # Reset to defaults
        print_banner()
        config = {
            'projectName': 'Cradle',
            'description': 'Enterprise Multi-Platform Architecture',
            'primaryColor': 'blue',
            'pages': [
                {'name': 'Dashboard', 'path': 'dashboard', 'icon': 'home', 'description': 'Main dashboard'},
                {'name': 'Settings', 'path': 'settings', 'icon': 'cog', 'description': 'Settings page'},
            ],
            'features': {'aiDisclosure': True, 'darkMode': True, 'multiTenant': True},
            'auth': {'defaultEmail': 'admin@example.com', 'defaultPassword': 'password'},
            'branding': {'logoText': None, 'tagline': None},
        }
        save_config(config)
        apply_config(config)
    else:
        # Interactive mode
        config = gather_config_interactive()
        print_summary(config)

        if prompt_yes_no("\nProceed with configuration?", True):
            save_config(config)
            apply_config(config)

            print(f"\n{Colors.GREEN}{'━' * 60}{Colors.NC}")
            print(f"{Colors.GREEN}✓ Configuration complete!{Colors.NC}")
            print(f"{Colors.GREEN}{'━' * 60}{Colors.NC}")
            print("\nNext steps:")
            print(f"  1. {Colors.CYAN}docker compose up{Colors.NC} - Start all services")
            print(f"  2. Open {Colors.CYAN}http://localhost:3010{Colors.NC} - View your app")
            print(f"  3. Login with {Colors.CYAN}admin@example.com / password{Colors.NC}")
            print("\nHappy building! 🚀\n")
        else:
            print_warning("Configuration cancelled.")


if __name__ == '__main__':
    main()
