from django.db import migrations

def create_skills(apps, schema_editor):
    Skill = apps.get_model('skills', 'Skill')
    
    skills = [
        # Programming Languages
        "Python", "JavaScript", "TypeScript", "Java", "C", "C++", "C#", "Ruby", "Go", "Rust",
        "Swift", "Kotlin", "PHP", "Perl", "Scala", "R", "MATLAB", "Dart", "Elixir", "Haskell",
        
        # Web Development
        "HTML", "CSS", "React", "Angular", "Vue.js", "Svelte", "Django", "Flask", "FastAPI",
        "Express.js", "Node.js", "Spring", "ASP.NET", "Laravel", "Ruby on Rails", "Next.js", "Nuxt.js",
        
        # Frontend Frameworks & Libraries
        "Bootstrap", "Tailwind CSS", "Material UI", "Chakra UI", "Sass", "Less", "Webpack", "Vite",
        
        # Backend & API
        "REST API", "GraphQL", "gRPC", "WebSocket", "OAuth", "JWT", "AWS Lambda", "Serverless",
        
        # Databases
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "SQLite", "Oracle",
        "Firebase", "Supabase", "Prisma",
        
        # Cloud & DevOps
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform", "Ansible", "Jenkins",
        "GitLab CI/CD", "GitHub Actions", "Nginx", "Apache", "Linux", "Bash", "PowerShell",
        
        # Data Science & ML
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Keras", "Pandas", "NumPy",
        "Scikit-learn", "Data Analysis", "Data Visualization", "Tableau", "Power BI", "NLP",
        
        # Mobile Development
        "React Native", "Flutter", "iOS Development", "Android Development", "Xamarin",
        
        # Tools & Version Control
        "Git", "GitHub", "GitLab", "Bitbucket", "SVN", "Jira", "Confluence", "VS Code",
        
        # Soft Skills
        "Team Leadership", "Project Management", "Agile", "Scrum", "Kanban", "Communication",
        "Problem Solving", "Critical Thinking", "Time Management", "Mentoring",
        
        # Security
        "Cybersecurity", "Penetration Testing", "OWASP", "SSL/TLS", "Security Auditing",
        
        # Other Technical Skills
        "Microservices", "System Design", "Architecture", "CI/CD", "Testing", "Unit Testing",
        "Integration Testing", "Selenium", "Jest", "Pytest", "Debugging", "Performance Optimization",
        "SEO", "Google Analytics", "Figma", "Sketch", "Adobe XD", "UI/UX Design"
    ]
    
    for skill_name in skills:
        Skill.objects.get_or_create(name=skill_name, defaults={'is_active': True})

def remove_skills(apps, schema_editor):
    Skill = apps.get_model('skills', 'Skill')
    Skill.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('skills', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_skills, remove_skills),
    ]
