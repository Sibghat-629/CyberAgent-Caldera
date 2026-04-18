const API_BASE = 'http://localhost:8000';
let selectedScenario = null;

const scenarioList = document.getElementById('scenarioList');
const terminal = document.getElementById('terminal');
const runBtn = document.getElementById('runBtn');
const httpStatus = document.getElementById('httpStatus');

async function init() {
    await checkStatus();
    await loadScenarios();
}

async function checkStatus() {
    try {
        const res = await fetch(`${API_BASE}/server-status`);
        if (res.ok) {
            httpStatus.classList.add('status-online');
        } else {
            httpStatus.classList.add('status-offline');
        }
    } catch (e) {
        httpStatus.classList.add('status-offline');
        addLog('System Error: Unable to connect to API backend.', 'error');
    }
}

async function loadScenarios() {
    try {
        const res = await fetch(`${API_BASE}/scenarios`);
        const scenarios = await res.json();
        
        scenarioList.innerHTML = '';
        scenarios.forEach(s => {
            const li = document.createElement('li');
            li.className = 'scenario-item';
            li.textContent = s.replace(/_/g, ' ');
            li.onclick = () => selectScenario(s, li);
            scenarioList.appendChild(li);
        });
    } catch (e) {
        addLog('Failed to load scenarios from server.', 'error');
    }
}

function selectScenario(name, el) {
    selectedScenario = name;
    document.querySelectorAll('.scenario-item').forEach(item => item.classList.remove('active'));
    el.classList.add('active');
    
    document.getElementById('currentScenarioTitle').textContent = name.replace(/_/g, ' ');
    runBtn.disabled = false;
    addLog(`Target locked: ${name}. Ready for deployment.`, 'info');
}

function addLog(message, type = 'info') {
    const line = document.createElement('div');
    line.className = `console-line line-${type}`;
    
    // Auto-detect agent names in logs for coloring
    if (message.includes('task_coordinator_agent')) type = 'coordinator';
    if (message.includes('text_analyst_agent') || message.includes('internet_agent')) type = 'agent';
    
    if (type === 'coordinator' || type === 'agent') {
        line.classList.add(`line-${type}`);
    }

    const timestamp = new Date().toLocaleTimeString([], { hour12: false });
    line.innerHTML = `<span style="color: #444; margin-right: 10px;">[${timestamp}]</span> ${message.replace(/\n/g, '<br>')}`;
    
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

runBtn.onclick = async () => {
    if (!selectedScenario) return;
    
    runBtn.disabled = true;
    runBtn.innerHTML = '<span class="loading-dots">Deploying</span>';
    addLog(`Initializing multi-agent handshake for ${selectedScenario}...`, 'info');
    
    try {
        const res = await fetch(`${API_BASE}/run/${selectedScenario}`, { method: 'POST' });
        const data = await res.json();
        
        if (data.output) {
            // Split output by lines or sections if possible
            const lines = data.output.split('********************************************************************************');
            lines.forEach(line => {
                if (line.trim()) addLog(line.trim(), 'info');
            });
        }
        
        if (data.error && data.error.trim()) {
            addLog(data.error.trim(), 'error');
        }
        
        addLog('Operation completed.', 'success');
    } catch (e) {
        addLog(`Execution failed: ${e.message}`, 'error');
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Re-initialize Agents';
    }
};

init();
setInterval(checkStatus, 30000); // Check status every 30s
