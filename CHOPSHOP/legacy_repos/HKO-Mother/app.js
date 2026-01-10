// HKO Metaverse Application
const app = {
  data: {
    files: [],
    codeSnippets: [],
    duplicates: [],
    architecture: [],
    projects: []
  },

  init() {
    this.loadData();
    this.setupEventListeners();
    this.renderDashboard();
  },

  loadData() {
    // Data is stored in memory only
    // All data persists during the session
  },

  saveData() {
    // Data is automatically saved in memory
    // No external storage needed
  },

  setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const page = e.target.dataset.page;
        this.navigateTo(page);
      });
    });

    // Forms
    document.getElementById('add-file-form').addEventListener('submit', (e) => this.handleAddFile(e));
    document.getElementById('bulk-import-form').addEventListener('submit', (e) => this.handleBulkImport(e));
    document.getElementById('add-code-form').addEventListener('submit', (e) => this.handleAddCode(e));
    document.getElementById('add-duplicate-form').addEventListener('submit', (e) => this.handleAddDuplicate(e));
    document.getElementById('add-architecture-form').addEventListener('submit', (e) => this.handleAddArchitecture(e));
    document.getElementById('add-project-form').addEventListener('submit', (e) => this.handleAddProject(e));
    document.getElementById('update-project-form').addEventListener('submit', (e) => this.handleUpdateProject(e));

    // Modal close on background click
    document.querySelectorAll('.modal').forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.classList.remove('active');
        }
      });
    });
  },

  navigateTo(page) {
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.remove('active');
      if (item.dataset.page === page) {
        item.classList.add('active');
      }
    });

    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));

    // Show selected page
    const pageElement = document.getElementById(`${page}-page`);
    if (pageElement) {
      pageElement.classList.remove('hidden');
    }

    // Render content for the page
    switch(page) {
      case 'dashboard':
        this.renderDashboard();
        break;
      case 'files':
        this.renderFiles();
        break;
      case 'code':
        this.renderCode();
        break;
      case 'duplicates':
        this.renderDuplicates();
        break;
      case 'architecture':
        this.renderArchitecture();
        break;
      case 'progress':
        this.renderProgress();
        break;
      case 'settings':
        this.renderSettings();
        break;
    }
  },

  renderDashboard() {
    // Update stats
    document.getElementById('stat-files').textContent = this.data.files.length;
    document.getElementById('stat-code').textContent = this.data.codeSnippets.length;
    document.getElementById('stat-duplicates').textContent = this.data.duplicates.length;
    document.getElementById('stat-architecture').textContent = this.data.architecture.length;
    
    const activeProjects = this.data.projects.filter(p => p.status === 'Active').length;
    document.getElementById('stat-projects').textContent = activeProjects;

    // Render active projects
    const projectsContainer = document.getElementById('dashboard-projects');
    const activeProjectsList = this.data.projects.filter(p => p.status === 'Active');
    
    if (activeProjectsList.length === 0) {
      projectsContainer.innerHTML = '<div class="empty-state"><p>No active projects. Create one to get started!</p></div>';
    } else {
      projectsContainer.innerHTML = activeProjectsList.slice(0, 5).map(project => {
        const percentage = Math.round((project.completedItems / project.totalItems) * 100);
        return `
          <div class="progress-card">
            <div class="progress-header">
              <div class="progress-info">
                <h4>${this.escapeHtml(project.name)}</h4>
                <div class="progress-meta">
                  <span>${this.escapeHtml(project.category)}</span>
                  <span class="priority-badge ${project.priority.toLowerCase()}">${this.escapeHtml(project.priority)}</span>
                </div>
              </div>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar" style="width: ${percentage}%">${percentage}%</div>
            </div>
            <p style="color: var(--color-text-secondary); font-size: var(--font-size-sm); margin-top: var(--space-8);">
              ${project.completedItems} of ${project.totalItems} items completed
            </p>
          </div>
        `;
      }).join('');
    }
  },

  renderFiles() {
    const tbody = document.getElementById('files-table-body');
    
    if (this.data.files.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--color-text-secondary);">No files tracked yet. Add your first file!</td></tr>';
      return;
    }

    tbody.innerHTML = this.data.files.map((file, index) => `
      <tr>
        <td>${this.escapeHtml(file.filename)}</td>
        <td>${this.escapeHtml(file.folder)}</td>
        <td>${this.escapeHtml(file.type)}</td>
        <td>${this.escapeHtml(file.status)}</td>
        <td>${new Date(file.dateAdded).toLocaleDateString()}</td>
        <td>
          <button class="btn btn-small btn-danger" onclick="app.deleteFile(${index})">Delete</button>
        </td>
      </tr>
    `).join('');
  },

  renderCode() {
    const tbody = document.getElementById('code-table-body');
    
    if (this.data.codeSnippets.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--color-text-secondary);">No code snippets yet. Add your first snippet!</td></tr>';
      return;
    }

    tbody.innerHTML = this.data.codeSnippets.map((snippet, index) => `
      <tr>
        <td><a href="#" onclick="app.viewCode(${index}); return false;" style="color: var(--color-primary);">${this.escapeHtml(snippet.title)}</a></td>
        <td>${this.escapeHtml(snippet.language)}</td>
        <td>${this.escapeHtml(snippet.dnaCategory)}</td>
        <td>${this.escapeHtml(snippet.module)}</td>
        <td>${snippet.productionReady ? '✓ Yes' : '✗ No'}</td>
        <td>
          <button class="btn btn-small btn-danger" onclick="app.deleteCode(${index})">Delete</button>
        </td>
      </tr>
    `).join('');
  },

  renderDuplicates() {
    const tbody = document.getElementById('duplicates-table-body');
    
    if (this.data.duplicates.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: var(--color-text-secondary);">No duplicates tracked yet.</td></tr>';
      return;
    }

    tbody.innerHTML = this.data.duplicates.map((dup, index) => `
      <tr>
        <td>${this.escapeHtml(dup.file1)}</td>
        <td>${this.escapeHtml(dup.file2)}</td>
        <td>${this.escapeHtml(dup.size)}</td>
        <td><span class="priority-badge ${dup.priority.toLowerCase()}">${this.escapeHtml(dup.priority)}</span></td>
        <td>
          <select onchange="app.updateDuplicateResolution(${index}, this.value)" style="padding: 6px; border: 1px solid var(--color-border); border-radius: var(--radius-base); background-color: var(--color-background); color: var(--color-text);">
            <option value="Pending" ${dup.resolution === 'Pending' ? 'selected' : ''}>Pending</option>
            <option value="Resolved" ${dup.resolution === 'Resolved' ? 'selected' : ''}>Resolved</option>
            <option value="Ignored" ${dup.resolution === 'Ignored' ? 'selected' : ''}>Ignored</option>
          </select>
        </td>
        <td>
          <button class="btn btn-small btn-danger" onclick="app.deleteDuplicate(${index})">Delete</button>
        </td>
      </tr>
    `).join('');
  },

  renderArchitecture() {
    const tbody = document.getElementById('architecture-table-body');
    
    if (this.data.architecture.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--color-text-secondary);">No architecture components yet. Start mapping your system!</td></tr>';
      return;
    }

    tbody.innerHTML = this.data.architecture.map((arch, index) => `
      <tr>
        <td>${this.escapeHtml(arch.layer)}</td>
        <td>${this.escapeHtml(arch.component)}</td>
        <td>${this.escapeHtml(arch.description)}</td>
        <td><span class="status-badge ${arch.status.toLowerCase().replace(' ', '-')}">${this.escapeHtml(arch.status)}</span></td>
        <td>
          <button class="btn btn-small btn-danger" onclick="app.deleteArchitecture(${index})">Delete</button>
        </td>
      </tr>
    `).join('');
  },

  renderProgress() {
    const container = document.getElementById('progress-list');
    
    if (this.data.projects.length === 0) {
      container.innerHTML = '<div class="empty-state"><h3>No Projects Yet</h3><p>Create your first project to start tracking progress!</p></div>';
      return;
    }

    container.innerHTML = this.data.projects.map((project, index) => {
      const percentage = Math.round((project.completedItems / project.totalItems) * 100);
      return `
        <div class="progress-card">
          <div class="progress-header">
            <div class="progress-info">
              <h4>${this.escapeHtml(project.name)}</h4>
              <div class="progress-meta">
                <span>${this.escapeHtml(project.category)}</span>
                <span class="priority-badge ${project.priority.toLowerCase()}">${this.escapeHtml(project.priority)}</span>
                <span class="status-badge ${project.status.toLowerCase().replace(' ', '-')}">${this.escapeHtml(project.status)}</span>
                ${project.targetDate ? `<span>Target: ${new Date(project.targetDate).toLocaleDateString()}</span>` : ''}
              </div>
            </div>
            <div class="progress-actions">
              <button class="btn btn-small btn-secondary" onclick="app.showUpdateProjectModal(${index})">Update</button>
              <button class="btn btn-small btn-danger" onclick="app.deleteProject(${index})">Delete</button>
            </div>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar" style="width: ${percentage}%">${percentage}%</div>
          </div>
          <p style="color: var(--color-text-secondary); font-size: var(--font-size-sm); margin-top: var(--space-8);">
            ${project.completedItems} of ${project.totalItems} items completed
          </p>
        </div>
      `;
    }).join('');
  },

  renderSettings() {
    document.getElementById('settings-files').textContent = this.data.files.length;
    document.getElementById('settings-code').textContent = this.data.codeSnippets.length;
    document.getElementById('settings-duplicates').textContent = this.data.duplicates.length;
    document.getElementById('settings-architecture').textContent = this.data.architecture.length;
    document.getElementById('settings-projects').textContent = this.data.projects.length;
  },

  // Modal functions
  showAddFileModal() {
    document.getElementById('add-file-form').reset();
    document.getElementById('add-file-modal').classList.add('active');
  },

  showBulkImportModal() {
    document.getElementById('bulk-import-form').reset();
    document.getElementById('import-result').classList.add('hidden');
    document.getElementById('bulk-import-modal').classList.add('active');
  },

  showAddCodeModal() {
    document.getElementById('add-code-form').reset();
    document.getElementById('add-code-modal').classList.add('active');
  },

  showAddDuplicateModal() {
    document.getElementById('add-duplicate-form').reset();
    document.getElementById('add-duplicate-modal').classList.add('active');
  },

  showAddArchitectureModal() {
    document.getElementById('add-architecture-form').reset();
    document.getElementById('add-architecture-modal').classList.add('active');
  },

  showAddProjectModal() {
    document.getElementById('add-project-form').reset();
    document.getElementById('add-project-modal').classList.add('active');
  },

  showUpdateProjectModal(index) {
    const project = this.data.projects[index];
    const form = document.getElementById('update-project-form');
    form.querySelector('[name="projectId"]').value = index;
    form.querySelector('[name="completedItems"]').value = project.completedItems;
    form.querySelector('[name="completedItems"]').max = project.totalItems;
    form.querySelector('[name="status"]').value = project.status;
    document.getElementById('update-project-modal').classList.add('active');
  },

  closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
  },

  viewCode(index) {
    const snippet = this.data.codeSnippets[index];
    const detailsDiv = document.getElementById('code-details');
    detailsDiv.innerHTML = `
      <div style="margin-bottom: 16px;">
        <p><strong>Title:</strong> ${this.escapeHtml(snippet.title)}</p>
        <p><strong>Language:</strong> ${this.escapeHtml(snippet.language)}</p>
        <p><strong>DNA Category:</strong> ${this.escapeHtml(snippet.dnaCategory)}</p>
        <p><strong>Module:</strong> ${this.escapeHtml(snippet.module)}</p>
        <p><strong>Production Ready:</strong> ${snippet.productionReady ? 'Yes' : 'No'}</p>
      </div>
      <div class="code-preview">${this.escapeHtml(snippet.code)}</div>
    `;
    document.getElementById('view-code-modal').classList.add('active');
  },

  // Form handlers
  handleAddFile(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const file = {
      filename: formData.get('filename'),
      folder: formData.get('folder'),
      type: formData.get('type'),
      status: formData.get('status'),
      dateAdded: new Date().toISOString()
    };
    this.data.files.push(file);
    this.saveData();
    this.closeModal('add-file-modal');
    this.renderFiles();
    this.renderDashboard();
  },

  handleBulkImport(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const files = e.target.querySelector('[name="files"]').files;
    const folder = formData.get('folder');
    const status = formData.get('status');
    
    if (!files || files.length === 0) {
      alert('Please select a folder to import');
      return;
    }

    let importCount = 0;
    for (let file of files) {
      const extension = file.name.substring(file.name.lastIndexOf('.'));
      this.data.files.push({
        filename: file.name,
        folder: folder,
        type: extension,
        status: status,
        dateAdded: new Date().toISOString()
      });
      importCount++;
    }

    this.saveData();
    
    const resultDiv = document.getElementById('import-result');
    resultDiv.textContent = `Successfully imported ${importCount} files!`;
    resultDiv.classList.remove('hidden');
    
    setTimeout(() => {
      this.closeModal('bulk-import-modal');
      this.renderFiles();
      this.renderDashboard();
    }, 2000);
  },

  handleAddCode(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const snippet = {
      title: formData.get('title'),
      language: formData.get('language'),
      dnaCategory: formData.get('dnaCategory'),
      module: formData.get('module'),
      code: formData.get('code'),
      productionReady: formData.get('productionReady') === 'on',
      dateAdded: new Date().toISOString()
    };
    this.data.codeSnippets.push(snippet);
    this.saveData();
    this.closeModal('add-code-modal');
    this.renderCode();
    this.renderDashboard();
  },

  handleAddDuplicate(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const duplicate = {
      file1: formData.get('file1'),
      file2: formData.get('file2'),
      size: formData.get('size'),
      priority: formData.get('priority'),
      resolution: formData.get('resolution'),
      dateAdded: new Date().toISOString()
    };
    this.data.duplicates.push(duplicate);
    this.saveData();
    this.closeModal('add-duplicate-modal');
    this.renderDuplicates();
    this.renderDashboard();
  },

  handleAddArchitecture(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const arch = {
      layer: formData.get('layer'),
      component: formData.get('component'),
      description: formData.get('description'),
      status: formData.get('status'),
      dateAdded: new Date().toISOString()
    };
    this.data.architecture.push(arch);
    this.saveData();
    this.closeModal('add-architecture-modal');
    this.renderArchitecture();
    this.renderDashboard();
  },

  handleAddProject(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const project = {
      name: formData.get('name'),
      category: formData.get('category'),
      totalItems: parseInt(formData.get('totalItems')),
      completedItems: parseInt(formData.get('completedItems')),
      priority: formData.get('priority'),
      status: formData.get('status'),
      targetDate: formData.get('targetDate'),
      dateCreated: new Date().toISOString()
    };
    this.data.projects.push(project);
    this.saveData();
    this.closeModal('add-project-modal');
    this.renderProgress();
    this.renderDashboard();
  },

  handleUpdateProject(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const index = parseInt(formData.get('projectId'));
    const completedItems = parseInt(formData.get('completedItems'));
    const status = formData.get('status');
    
    if (completedItems > this.data.projects[index].totalItems) {
      alert('Completed items cannot exceed total items');
      return;
    }

    this.data.projects[index].completedItems = completedItems;
    this.data.projects[index].status = status;
    
    this.saveData();
    this.closeModal('update-project-modal');
    this.renderProgress();
    this.renderDashboard();
  },

  // Delete functions
  deleteFile(index) {
    if (confirm('Are you sure you want to delete this file?')) {
      this.data.files.splice(index, 1);
      this.saveData();
      this.renderFiles();
      this.renderDashboard();
    }
  },

  deleteCode(index) {
    if (confirm('Are you sure you want to delete this code snippet?')) {
      this.data.codeSnippets.splice(index, 1);
      this.saveData();
      this.renderCode();
      this.renderDashboard();
    }
  },

  deleteDuplicate(index) {
    if (confirm('Are you sure you want to delete this duplicate entry?')) {
      this.data.duplicates.splice(index, 1);
      this.saveData();
      this.renderDuplicates();
      this.renderDashboard();
    }
  },

  deleteArchitecture(index) {
    if (confirm('Are you sure you want to delete this architecture component?')) {
      this.data.architecture.splice(index, 1);
      this.saveData();
      this.renderArchitecture();
      this.renderDashboard();
    }
  },

  deleteProject(index) {
    if (confirm('Are you sure you want to delete this project?')) {
      this.data.projects.splice(index, 1);
      this.saveData();
      this.renderProgress();
      this.renderDashboard();
    }
  },

  updateDuplicateResolution(index, resolution) {
    this.data.duplicates[index].resolution = resolution;
    this.saveData();
  },

  // Data management
  exportData() {
    const dataStr = JSON.stringify(this.data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `hko_metaverse_export_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  },

  confirmResetData() {
    if (confirm('Are you sure you want to reset ALL data? This action cannot be undone.')) {
      if (confirm('This will permanently delete all files, code snippets, duplicates, architecture, and projects. Continue?')) {
        this.data = {
          files: [],
          codeSnippets: [],
          duplicates: [],
          architecture: [],
          projects: []
        };
        this.saveData();
        this.navigateTo('dashboard');
        alert('All data has been reset.');
      }
    }
  },

  escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
};

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => app.init());
} else {
  app.init();
}