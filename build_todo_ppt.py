import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = pptx.Presentation('DevOps PPT.pptx')
    print(f"Loaded template with {len(prs.slides)} slides.")

    # 1. Global replacements across all paragraphs & runs
    REPLACEMENTS = [
        ("for the Sudoku Web Application", "for the Static To-Do Web Application"),
        ("Sudoku Web App", "To-Do Web App"),
        ("Sudoku Web Application", "To-Do Web Application"),
        ("Flask Sudoku Web Application", "Static To-Do Web Application"),
        ("Sudoku-Game", "todo_aws"),
        ("github.com/26sakthi/Sudoku-Game", "github.com/Purusouthanan/todo_aws"),
        ("github.com/26sakthi", "github.com/Purusouthanan"),
        ("26sakthi", "Purusouthanan"),
        ("SAKTHIVEL R", "PURUSOUTHANAN"),
        ("Python 3.11 with Flask & Jinja2 templating.", "HTML5, Modern CSS3 & Vanilla JavaScript (ES6) served via Nginx."),
        ("DYNAMIC ENVIRONMENT INJECTIONS", "CORE APPLICATION CAPABILITIES"),
        ("SUDOKU_DIFFICULTY", "TASK_MANAGEMENT"),
        ("SUDOKU_SIZE", "STATE_PERSISTENCE"),
        ("SUDOKU_MAX_ATTEMPTS", "WEB_RUNTIME"),
        ("medium", "Dynamic CRUD"),
        ("sudoku-cluster", "minikube-cluster"),
        ("sudoku-app:1.0", "todo-app:latest"),
        ("sudoku-app", "todo-app"),
        ("sudoku-deployment", "todo-app-deployment"),
        ("sudoku-service", "todo-app-service"),
        ("sudoku-config", "todo-config"),
        ("sudoku-ansible:1.0", "todo-ansible:1.0"),
        ("sudoku-ansible", "todo-ansible"),
        ("sudoku", "todo"),
        ("Sudoku", "To-Do"),
        ("tehcyx/kind", "scott-the-programmer/minikube"),
        ("Kind / K8s", "Minikube / K8s"),
        ("Kind cluster", "Minikube cluster"),
        ("Kind clusters", "Minikube clusters"),
        ("Kind worker node’s", "Minikube cluster's"),
        ("Kind worker", "Minikube"),
        ("Kind API", "Minikube API"),
        ("kind load docker-image", "minikube image load"),
        ("kind get clusters", "minikube status"),
        ("kind get kubeconfig", "kubectl config view"),
        ("Load Image into Kind", "Load Image into Minikube"),
        ("Ansible ConfigMap", "Ansible Setup"),
        ("Ansible Inject ConfigMap", "Ansible Setup & Tools"),
        ("Kind", "Minikube"),
        ("kind", "minikube"),
        ("kubernetes/", "k8s/"),
    ]

    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    # check runs first
                    for old_val, new_val in REPLACEMENTS:
                        if old_val in p.text:
                            p.text = p.text.replace(old_val, new_val)

    # 2. Specific slide updates for professional accuracy

    # Slide 1: Tech stack badge
    s1 = prs.slides[0]
    for shape in s1.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if p.text.strip() == "Python":
                    p.text = "HTML / JS"

    # Slide 3: Directory structure
    s3 = prs.slides[2]
    for shape in s3.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "app.py" in p.text or "requirements.txt" in p.text:
                    p.text = (
                        "app/\n"
                        "├── index.html\n"
                        "│   Semantic HTML5 task UI markup\n"
                        "├── style.css\n"
                        "│   Responsive styling & modern design\n"
                        "├── app.js\n"
                        "│   Task CRUD logic, filters & storage\n"
                        "└── Dockerfile\n"
                        "    Nginx alpine container build spec"
                    )

    # Slide 4: Dockerfile and Specs
    s4 = prs.slides[3]
    for shape in s4.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "python:3.11-slim" in p.text:
                    p.text = (
                        "Base image: nginx:alpine keeps the container ultralight (<25MB) and blazing fast.\n"
                        "Static assets copied directly into /usr/share/nginx/html for zero-overhead serving.\n"
                        "Exposes port 80 for standard HTTP traffic routing.\n"
                        "Immutable container artifact: identical behavior in local testing and cluster rollout."
                    )
                elif "WORKDIR /app" in p.text or "EXPOSE 5000" in p.text:
                    p.text = (
                        "FROM nginx:alpine\n"
                        "WORKDIR /usr/share/nginx/html\n"
                        "COPY . .\n"
                        "EXPOSE 80\n"
                        "CMD [\"nginx\", \"-g\", \"daemon off;\"]"
                    )
                elif "docker run -d -p 5000:5000" in p.text or "cd app" in p.text:
                    p.text = (
                        "# Navigate & build the Docker image\n"
                        "cd app\n"
                        "docker build -t todo-app:latest .\n\n"
                        "# Verify the built image\n"
                        "docker images | grep todo-app\n\n"
                        "# Test container locally\n"
                        "docker run -d -p 8080:80 --name test-todo todo-app:latest"
                    )

    # Slide 7: K8s Port and Service type
    s7 = prs.slides[6]
    for shape in s7.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "ClusterIP" in p.text:
                    p.text = p.text.replace("ClusterIP", "NodePort")
                if "port 5000" in p.text:
                    p.text = p.text.replace("port 5000", "port 80 (NodePort 30080)")

    # Slide 8: Ansible playbook info
    s8 = prs.slides[7]
    for shape in s8.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "playbook.yml" in p.text:
                    p.text = p.text.replace("playbook.yml", "jenkins-setup.yml")
                if "TERMINAL — RUN PLAYBOOK (POWERSHELL)" in p.text:
                    p.text = "TERMINAL — RUN PLAYBOOK"
                if "Set-Content" in p.text or "$kc =" in p.text:
                    p.text = (
                        "# 1. Inspect inventory file\n"
                        "cat ansible/inventory.ini\n\n"
                        "# 2. Run Ansible playbook to provision Jenkins\n"
                        "ansible-playbook -i ansible/inventory.ini \\\n"
                        "  ansible/jenkins-setup.yml\n\n"
                        "# 3. Retrieve Jenkins initial admin password\n"
                        "docker exec -it jenkins \\\n"
                        "  cat /var/jenkins_home/secrets/initialAdminPassword"
                    )

    # Slide 9: Jenkinsfile
    s9 = prs.slides[8]
    for shape in s9.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "pipeline {" in p.text:
                    p.text = (
                        "pipeline {\n"
                        "  agent any\n"
                        "  stages {\n"
                        "    stage('Checkout') {\n"
                        "      steps { echo 'Checking out source code...' }\n"
                        "    }\n"
                        "    stage('Build Image') {\n"
                        "      steps {\n"
                        "        dir('app') {\n"
                        "          sh 'docker build -t todo-app:latest .'\n"
                        "        }\n"
                        "      }\n"
                        "    }\n"
                        "    stage('Deploy to K8s') {\n"
                        "      steps {\n"
                        "        dir('k8s') {\n"
                        "          sh 'kubectl apply -f deployment.yaml -f service.yaml'\n"
                        "        }\n"
                        "      }\n"
                        "    }\n"
                        "  }\n"
                        "}"
                    )

    # Slide 10: Verification commands
    s10 = prs.slides[9]
    for shape in s10.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "kubectl describe configmap" in p.text or "5000:5000" in p.text:
                    p.text = (
                        "# 1. Check Minikube node readiness\n"
                        "kubectl get nodes\n\n"
                        "# 2. Verify Pod status (must be 1/1 Running)\n"
                        "kubectl get pods -l app=todo-app\n\n"
                        "# 3. Retrieve service URL from Minikube\n"
                        "minikube service todo-app-service --url\n\n"
                        "# 4. Validate HTTP response status\n"
                        "curl -I $(minikube service todo-app-service --url)"
                    )

    # Slide 11: Live Demo & Working UI Dashboard
    s11 = prs.slides[10]
    for shape in s11.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                if "Playing To-Do in the browser" in p.text or "Playing Sudoku" in p.text:
                    p.text = "Interactive Working & End-to-End User Experience"
                elif "5000" in p.text:
                    p.text = "http://<minikube-ip>:30080"
                elif "FEATURES" in p.text:
                    p.text = "HOW THE SYSTEM OPERATES"
                elif "Dynamic grid generation" in p.text:
                    p.text = (
                        "1. User Action: Enter tasks, assign priorities (High/Med/Low), and add items.\n"
                        "2. Dynamic DOM Engine: JavaScript renders task cards with instant visual badges.\n"
                        "3. Filter & Counter Logic: Real-time tabs (All / Active / Completed) and task counts.\n"
                        "4. Storage Sync: Browser LocalStorage preserves tasks across tab & browser reloads.\n"
                        "5. Kubernetes Delivery: Replicated Nginx pods ensure sub-10ms response times."
                    )

    # Clean old sudoku board shapes if any still present
    shapes_to_remove = []
    for sp in s11.shapes:
        if sp.left >= Inches(6.8) and sp.top >= Inches(1.5) and sp.top <= Inches(6.8):
            shapes_to_remove.append(sp)

    for sp in shapes_to_remove:
        sp_elem = sp._element
        sp_elem.getparent().remove(sp_elem)

    # Add To-Do Application Mockup Dashboard card
    card_bg = s11.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(6.8), Inches(1.5), Inches(5.8), Inches(5.0)
    )
    card_bg.fill.solid()
    card_bg.fill.fore_color.rgb = RGBColor(26, 38, 57)  # Dark slate blue
    card_bg.line.color.rgb = RGBColor(91, 124, 153)     # Border matching template
    card_bg.line.width = Pt(1.5)

    # Card Title Bar
    title_box = s11.shapes.add_textbox(Inches(7.1), Inches(1.7), Inches(5.2), Inches(0.5))
    tf_tb = title_box.text_frame
    p_tb = tf_tb.paragraphs[0]
    p_tb.text = "⚡ TO-DO APP — LIVE CLUSTER DASHBOARD"
    p_tb.font.size = Pt(12)
    p_tb.font.bold = True
    p_tb.font.color.rgb = RGBColor(255, 255, 255)

    # Input Box Mockup
    input_box = s11.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(7.1), Inches(2.3), Inches(3.8), Inches(0.45)
    )
    input_box.fill.solid()
    input_box.fill.fore_color.rgb = RGBColor(15, 23, 42)
    input_box.line.color.rgb = RGBColor(62, 90, 114)
    tf_ib = input_box.text_frame
    p_ib = tf_ib.paragraphs[0]
    p_ib.text = " Deploy monitoring stack to K8s..."
    p_ib.font.size = Pt(10)
    p_ib.font.color.rgb = RGBColor(160, 174, 192)

    # Add Task Button Mockup
    btn_box = s11.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(11.0), Inches(2.3), Inches(1.3), Inches(0.45)
    )
    btn_box.fill.solid()
    btn_box.fill.fore_color.rgb = RGBColor(91, 124, 153)
    btn_box.line.fill.background()
    tf_btn = btn_box.text_frame
    p_btn = tf_btn.paragraphs[0]
    p_btn.text = "+ Add Task"
    p_btn.font.size = Pt(10)
    p_btn.font.bold = True
    p_btn.alignment = PP_ALIGN.CENTER
    p_btn.font.color.rgb = RGBColor(255, 255, 255)

    # Task Items List
    tasks = [
        ("✔", "Provision Minikube Cluster with Terraform", "High", RGBColor(56, 161, 105), True),
        ("✔", "Install & Configure Jenkins via Ansible", "High", RGBColor(56, 161, 105), True),
        ("✔", "Build & Deploy To-Do Pods to Kubernetes", "Medium", RGBColor(56, 161, 105), True),
        ("○", "Expose App via NodePort & Validate Probes", "Medium", RGBColor(226, 232, 240), False),
        ("○", "Add Automated Prometheus Metric Scraping", "Low", RGBColor(160, 174, 192), False)
    ]

    top_offset = 2.95
    for status_icon, task_title, priority, text_color, is_done in tasks:
        row_shape = s11.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Inches(7.1), Inches(top_offset), Inches(5.2), Inches(0.55)
        )
        row_shape.fill.solid()
        row_shape.fill.fore_color.rgb = RGBColor(20, 30, 48) if is_done else RGBColor(15, 23, 42)
        row_shape.line.color.rgb = RGBColor(45, 65, 85)
        row_shape.line.width = Pt(1)

        tf_row = row_shape.text_frame
        p_row = tf_row.paragraphs[0]
        p_row.text = f" {status_icon}  {task_title}"
        p_row.font.size = Pt(10)
        p_row.font.color.rgb = text_color
        p_row.font.bold = is_done

        badge = s11.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(11.3), Inches(top_offset + 0.12), Inches(0.85), Inches(0.3)
        )
        badge.fill.solid()
        if priority == "High":
            badge.fill.fore_color.rgb = RGBColor(197, 48, 48)
        elif priority == "Medium":
            badge.fill.fore_color.rgb = RGBColor(214, 158, 46)
        else:
            badge.fill.fore_color.rgb = RGBColor(74, 85, 104)
        badge.line.fill.background()
        tf_b = badge.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.text = priority
        p_b.font.size = Pt(8)
        p_b.font.bold = True
        p_b.alignment = PP_ALIGN.CENTER
        p_b.font.color.rgb = RGBColor(255, 255, 255)

        top_offset += 0.62

    stats_box = s11.shapes.add_textbox(Inches(7.1), Inches(6.05), Inches(5.2), Inches(0.35))
    tf_st = stats_box.text_frame
    p_st = tf_st.paragraphs[0]
    p_st.text = "📊 Total Tasks: 5   |   Completed: 3   |   Active: 2   |   LocalStorage: Synchronized"
    p_st.font.size = Pt(8.5)
    p_st.font.color.rgb = RGBColor(160, 174, 192)

    # Save output presentation
    output_path = 'todo_ppt.pptx'
    prs.save(output_path)
    print(f"Successfully generated and saved {output_path}!")

if __name__ == '__main__':
    build_presentation()
