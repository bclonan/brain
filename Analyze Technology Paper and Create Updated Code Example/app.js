/* 
 * Fibonacci Grid System - Frontend JavaScript
 * 
 * This file contains the JavaScript code for the Fibonacci Grid System frontend.
 * It handles the interaction with the backend API and provides the interactive
 * functionality for the UI.
 */

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State Management
const appState = {
    currentSection: 'grid-explorer',
    grid: {
        currentGridId: null,
        grids: {},
        viewSettings: {
            startRow: 0,
            startCol: 0,
            rows: 10,
            cols: 10
        },
        effects: {
            lightning: {
                enabled: false,
                row: 5,
                col: 5
            },
            whirlwind: {
                enabled: false,
                row: 5,
                col: 5,
                intensity: 0.8
            }
        }
    },
    observer: {
        currentObserverId: null,
        observers: {},
        transformationMatrix: Array(10).fill().map(() => Array(1).fill(0))
    },
    frequency: {
        currentProcessorId: null,
        processors: {},
        timeline: []
    },
    compression: {
        currentDbId: null,
        dbs: {},
        lastCompressed: null,
        lastDecompressed: null
    }
};

// Initialize identity matrix for default observer
for (let i = 0; i < 10; i++) {
    appState.observer.transformationMatrix[i][0] = i + 1;
}

// DOM Ready Handler
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

// App Initialization
function initializeApp() {
    // Set up navigation
    setupNavigation();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize components
    initializeGridExplorer();
    initializeObserverPerspectives();
    initializeFrequencyAnalyzer();
    initializeCompressionLab();
    initializeDemos();
    
    // Create initial objects
    createInitialObjects();
}

// Navigation Setup
function setupNavigation() {
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update active link
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Show corresponding section
            const sectionId = link.getAttribute('data-section');
            showSection(sectionId);
        });
    });
}

// Show Section
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Update current section
    appState.currentSection = sectionId;
    
    // Update sidebar content based on section
    updateSidebar(sectionId);
}

// Update Sidebar
function updateSidebar(sectionId) {
    const sidebarContent = document.getElementById('sidebar-content');
    
    // Clear current content
    sidebarContent.innerHTML = '';
    
    // Load section-specific sidebar content
    switch (sectionId) {
        case 'grid-explorer':
            sidebarContent.innerHTML = `
                <div class="d-grid gap-2">
                    <button id="create-grid-btn" class="btn btn-primary">
                        <i class="bi bi-grid-3x3-gap-fill me-2"></i>Create New Grid
                    </button>
                    <button id="load-grid-btn" class="btn btn-secondary">
                        <i class="bi bi-folder2-open me-2"></i>Load Existing Grid
                    </button>
                </div>
                
                <hr>
                
                <div id="grid-controls" class="mt-3">
                    <h6>Grid Settings</h6>
                    <div class="mb-3">
                        <label for="grid-size" class="form-label">Grid Size</label>
                        <input type="number" class="form-control" id="grid-size" value="${appState.grid.viewSettings.rows}" min="10" max="1000">
                    </div>
                    <div class="mb-3">
                        <label for="view-start-row" class="form-label">Start Row</label>
                        <input type="number" class="form-control" id="view-start-row" value="${appState.grid.viewSettings.startRow}" min="0">
                    </div>
                    <div class="mb-3">
                        <label for="view-start-col" class="form-label">Start Column</label>
                        <input type="number" class="form-control" id="view-start-col" value="${appState.grid.viewSettings.startCol}" min="0">
                    </div>
                    <div class="mb-3">
                        <label for="view-rows" class="form-label">Rows to View</label>
                        <input type="number" class="form-control" id="view-rows" value="${appState.grid.viewSettings.rows}" min="1" max="50">
                    </div>
                    <div class="mb-3">
                        <label for="view-cols" class="form-label">Columns to View</label>
                        <input type="number" class="form-control" id="view-cols" value="${appState.grid.viewSettings.cols}" min="1" max="50">
                    </div>
                    <div class="d-grid">
                        <button id="update-view-btn" class="btn btn-success">
                            <i class="bi bi-eye me-2"></i>Update View
                        </button>
                    </div>
                </div>
                
                <div id="effect-controls" class="mt-3">
                    <h6>Effects</h6>
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="lightning-effect-toggle" ${appState.grid.effects.lightning.enabled ? 'checked' : ''}>
                        <label class="form-check-label" for="lightning-effect-toggle">Lightning Effect</label>
                    </div>
                    <div id="lightning-controls" class="ps-4 mb-3" style="display: ${appState.grid.effects.lightning.enabled ? 'block' : 'none'};">
                        <div class="mb-2">
                            <label for="lightning-row" class="form-label">Target Row</label>
                            <input type="number" class="form-control" id="lightning-row" value="${appState.grid.effects.lightning.row}" min="0">
                        </div>
                        <div class="mb-2">
                            <label for="lightning-col" class="form-label">Target Column</label>
                            <input type="number" class="form-control" id="lightning-col" value="${appState.grid.effects.lightning.col}" min="0">
                        </div>
                    </div>
                    
                    <div class="form-check form-switch mb-3">
                        <input class="form-check-input" type="checkbox" id="whirlwind-effect-toggle" ${appState.grid.effects.whirlwind.enabled ? 'checked' : ''}>
                        <label class="form-check-label" for="whirlwind-effect-toggle">Whirlwind Effect</label>
                    </div>
                    <div id="whirlwind-controls" class="ps-4" style="display: ${appState.grid.effects.whirlwind.enabled ? 'block' : 'none'};">
                        <div class="mb-2">
                            <label for="whirlwind-row" class="form-label">Center Row</label>
                            <input type="number" class="form-control" id="whirlwind-row" value="${appState.grid.effects.whirlwind.row}" min="0">
                        </div>
                        <div class="mb-2">
                            <label for="whirlwind-col" class="form-label">Center Column</label>
                            <input type="number" class="form-control" id="whirlwind-col" value="${appState.grid.effects.whirlwind.col}" min="0">
                        </div>
                        <div class="mb-2">
                            <label for="whirlwind-intensity" class="form-label">Intensity</label>
                            <input type="range" class="form-range" id="whirlwind-intensity" min="0" max="1" step="0.1" value="${appState.grid.effects.whirlwind.intensity}">
                        </div>
                    </div>
                </div>
            `;
            break;
            
        case 'observer-perspectives':
            sidebarContent.innerHTML = `
                <div class="d-grid gap-2">
                    <button id="create-observer-btn" class="btn btn-primary">
                        <i class="bi bi-person-plus me-2"></i>Create New Observer
                    </button>
                    <button id="load-observer-btn" class="btn btn-secondary">
                        <i class="bi bi-folder2-open me-2"></i>Load Existing Observer
                    </button>
                </div>
                
                <hr>
                
                <div id="observer-grid-selection" class="mt-3">
                    <h6>Select Grid to Observe</h6>
                    <select class="form-select" id="grid-selector">
                        <option value="">Select a grid...</option>
                    </select>
                </div>
                
                <hr>
                
                <div id="matrix-controls" class="mt-3">
                    <h6>Matrix Operations</h6>
                    <div class="mb-3">
                        <button id="identity-matrix-btn" class="btn btn-sm btn-outline-primary">Identity</button>
                        <button id="shift-matrix-btn" class="btn btn-sm btn-outline-primary">Shift</button>
                        <button id="invert-matrix-btn" class="btn btn-sm btn-outline-primary">Invert</button>
                    </div>
                    <div class="mb-3">
                        <label for="shift-value" class="form-label">Shift Value</label>
                        <input type="number" class="form-control" id="shift-value" value="1" min="1" max="9">
                    </div>
                </div>
            `;
            
            // Populate grid selector
            setTimeout(() => {
                populateGridSelector();
            }, 100);
            break;
            
        case 'frequency-analyzer':
            sidebarContent.innerHTML = `
                <div class="d-grid gap-2">
                    <button id="create-processor-btn" class="btn btn-primary">
                        <i class="bi bi-soundwave me-2"></i>Create New Processor
                    </button>
                    <button id="load-processor-btn" class="btn btn-secondary">
                        <i class="bi bi-folder2-open me-2"></i>Load Existing Processor
                    </button>
                </div>
                
                <hr>
                
                <div id="frequency-controls" class="mt-3">
                    <h6>Beat Pattern Generator</h6>
                    <div class="mb-3">
                        <label for="frequency1" class="form-label">Frequency 1 (Hz)</label>
                        <input type="number" class="form-control" id="frequency1" value="400" min="1" max="1000">
                    </div>
                    <div class="mb-3">
                        <label for="frequency2" class="form-label">Frequency 2 (Hz)</label>
                        <input type="number" class="form-control" id="frequency2" value="405" min="1" max="1000">
                    </div>
                    <div class="mb-3">
                        <label for="duration" class="form-label">Duration (seconds)</label>
                        <input type="number" class="form-control" id="duration" value="1.0" min="0.1" max="10" step="0.1">
                    </div>
                    <div class="d-grid">
                        <button id="generate-beat-btn" class="btn btn-success">
                            <i class="bi bi-soundwave me-2"></i>Generate Beat Pattern
                        </button>
                    </div>
                </div>
            `;
            break;
            
        case 'compression-lab':
            sidebarContent.innerHTML = `
                <div class="d-grid gap-2">
                    <button id="create-db-btn" class="btn btn-primary">
                        <i class="bi bi-database-add me-2"></i>Create New Database
                    </button>
                    <button id="load-db-btn" class="btn btn-secondary">
                        <i class="bi bi-folder2-open me-2"></i>Load Existing Database
                    </button>
                </div>
                
                <hr>
                
                <div id="compression-controls" class="mt-3">
                    <h6>Compression Settings</h6>
                    <div class="mb-3">
                        <label for="grid-size-db" class="form-label">Grid Size</label>
                        <input type="number" class="form-control" id="grid-size-db" value="100" min="10" max="1000">
                    </div>
                    <div class="mb-3">
                        <label for="sample-text" class="form-label">Sample Text</label>
                        <select class="form-select" id="sample-text">
                            <option value="">Select sample text...</option>
                            <option value="lorem">Lorem Ipsum</option>
                            <option value="code">Code Sample</option>
                            <option value="json">JSON Data</option>
                        </select>
                    </div>
                    <div class="d-grid">
                        <button id="load-sample-btn" class="btn btn-outline-primary">
                            <i class="bi bi-file-text me-2"></i>Load Sample
                        </button>
                    </div>
                </div>
                
                <hr>
                
                <div id="benchmark-controls" class="mt-3">
                    <h6>Benchmarking</h6>
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" id="benchmark-gzip">
                        <label class="form-check-label" for="benchmark-gzip">Compare with GZIP</label>
                    </div>
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" id="benchmark-lz77">
                        <label class="form-check-label" for="benchmark-lz77">Compare with LZ77</label>
                    </div>
                    <div class="d-grid">
                        <button id="run-benchmark-btn" class="btn btn-outline-success">
                            <i class="bi bi-speedometer2 me-2"></i>Run Benchmark
                        </button>
                    </div>
                </div>
            `;
            break;
            
        case 'demos':
            sidebarContent.innerHTML = `
                <div class="d-grid gap-2">
                    <button id="refresh-demos-btn" class="btn btn-primary">
                        <i class="bi bi-arrow-clockwise me-2"></i>Refresh Demos
                    </button>
                </div>
                
                <hr>
                
                <div id="demo-controls" class="mt-3">
                    <h6>Demo Settings</h6>
                    <div class="mb-3">
                        <label for="demo-complexity" class="form-label">Complexity</label>
                        <select class="form-select" id="demo-complexity">
                            <option value="simple">Simple</option>
                            <option value="medium" selected>Medium</option>
                            <option value="complex">Complex</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="demo-speed" class="form-label">Animation Speed</label>
                        <input type="range" class="form-range" id="demo-speed" min="0.5" max="2" step="0.1" value="1">
                    </div>
                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" id="demo-auto-advance" checked>
                        <label class="form-check-label" for="demo-auto-advance">Auto-advance steps</label>
                    </div>
                </div>
                
                <hr>
                
                <div id="demo-info" class="mt-3">
                    <h6>Demo Information</h6>
                    <div class="alert alert-info">
                        <p class="mb-0">Select a demo from the main panel to view details and controls.</p>
                    </div>
                </div>
            `;
            break;
    }
    
    // Re-attach event listeners
    setupEventListeners();
}

// Setup Event Listeners
function setupEventListeners() {
    // Grid Explorer
    const createGridBtn = document.getElementById('create-grid-btn');
    if (createGridBtn) {
        createGridBtn.addEventListener('click', () => {
            const modal = new bootstrap.Modal(document.getElementById('create-grid-modal'));
            modal.show();
        });
    }
    
    const confirmCreateGridBtn = document.getElementById('confirm-create-grid');
    if (confirmCreateGridBtn) {
        confirmCreateGridBtn.addEventListener('click', () => {
            const size = parseInt(document.getElementById('new-grid-size').value);
            createGrid(size);
            bootstrap.Modal.getInstance(document.getElementById('create-grid-modal')).hide();
        });
    }
    
    const updateViewBtn = document.getElementById('update-view-btn');
    if (updateViewBtn) {
        updateViewBtn.addEventListener('click', updateGridView);
    }
    
    const lightningToggle = document.getElementById('lightning-effect-toggle');
    if (lightningToggle) {
        lightningToggle.addEventListener('change', () => {
            appState.grid.effects.lightning.enabled = lightningToggle.checked;
            document.getElementById('lightning-controls').style.display = lightningToggle.checked ? 'block' : 'none';
            updateGridView();
        });
    }
    
    const whirlwindToggle = document.getElementById('whirlwind-effect-toggle');
    if (whirlwindToggle) {
        whirlwindToggle.addEventListener('change', () => {
            appState.grid.effects.whirlwind.enabled = whirlwindToggle.checked;
            document.getElementById('whirlwind-controls').style.display = whirlwindToggle.checked ? 'block' : 'none';
            updateGridView();
        });
    }
    
    // Observer Perspectives
    const createObserverBtn = document.getElementById('create-observer-btn');
    if (createObserverBtn) {
        createObserverBtn.addEventListener('click', () => {
            const modal = new bootstrap.Modal(document.getElementById('create-observer-modal'));
            modal.show();
        });
    }
    
    const confirmCreateObserverBtn = document.getElementById('confirm-create-observer');
    if (confirmCreateObserverBtn) {
        confirmCreateObserverBtn.addEventListener('click', () => {
            const name = document.getElementById('new-observer-name').value;
            const focusLayers = Array.from(document.getElementById('new-focus-layers').selectedOptions).map(option => parseInt(option.value));
            
            let transformationMatrix = null;
            const transformationType = document.querySelector('input[name="transformation-type"]:checked').id;
            
            if (transformationType === 'shift-transform') {
                const shiftAmount = parseInt(document.getElementById('shift-amount').value);
                transformationMatrix = createShiftMatrix(shiftAmount);
            } else if (transformationType === 'custom-transform') {
                // Custom matrix would be handled here
                transformationMatrix = null;
            }
            
            createObserver(name, focusLayers, transformationMatrix);
            bootstrap.Modal.getInstance(document.getElementById('create-observer-modal')).hide();
        });
    }
    
    // Transformation type radio buttons
    const transformationTypeRadios = document.querySelectorAll('input[name="transformation-type"]');
    if (transformationTypeRadios.length > 0) {
        transformationTypeRadios.forEach(radio => {
            radio.addEventListener('change', () => {
                document.getElementById('shift-options').style.display = 
                    radio.id === 'shift-transform' ? 'block' : 'none';
            });
        });
    }
    
    // Matrix operation buttons
    const identityMatrixBtn = document.getElementById('identity-matrix-btn');
    if (identityMatrixBtn) {
        identityMatrixBtn.addEventListener('click', () => {
            appState.observer.transformationMatrix = createIdentityMatrix();
            updateTransformationMatrixDisplay();
        });
    }
    
    const shiftMatrixBtn = document.getElementById('shift-matrix-btn');
    if (shiftMatrixBtn) {
        shiftMatrixBtn.addEventListener('click', () => {
            const shiftValue = parseInt(document.getElementById('shift-value').value);
            appState.observer.transformationMatrix = createShiftMatrix(shiftValue);
            updateTransformationMatrixDisplay();
        });
    }
    
    const invertMatrixBtn = document.getElementById('invert-matrix-btn');
    if (invertMatrixBtn) {
        invertMatrixBtn.addEventListener('click', () => {
            appState.observer.transformationMatrix = createInvertMatrix();
            updateTransformationMatrixDisplay();
        });
    }
    
    // Frequency Analyzer
    const generateBeatBtn = document.getElementById('generate-beat-btn');
    if (generateBeatBtn) {
        generateBeatBtn.addEventListener('click', generateBeatPattern);
    }
    
    // Compression Lab
    const compressBtn = document.getElementById('compress-btn');
    if (compressBtn) {
        compressBtn.addEventListener('click', compressData);
    }
    
    const decompressBtn = document.getElementById('decompress-btn');
    if (decompressBtn) {
        decompressBtn.addEventListener('click', decompressData);
    }
    
    const loadSampleBtn = document.getElementById('load-sample-btn');
    if (loadSampleBtn) {
        loadSampleBtn.addEventListener('click', loadSampleText);
    }
    
    // Demo buttons
    const demoButtons = document.querySelectorAll('[id^="launch-"][id$="-demo"]');
    demoButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const demoType = e.target.id.replace('launch-', '').replace('-demo', '');
            launchDemo(demoType);
        });
    });
}

// Initialize Grid Explorer
function initializeGridExplorer() {
    // Initial grid visualization placeholder
    document.getElementById('grid-visualization').innerHTML = `
        <div class="text-center py-5">
            <p class="text-muted">Create or load a grid to begin</p>
        </div>
    `;
}

// Initialize Observer Perspectives
function initializeObserverPerspectives() {
    // Initialize transformation matrix display
    updateTransformationMatrixDisplay();
}

// Initialize Frequency Analyzer
function initializeFrequencyAnalyzer() {
    // Initial frequency visualization placeholder
    document.getElementById('frequency-visualization').innerHTML = `
        <div class="text-center py-5">
            <p class="text-muted">Generate a beat pattern or create an entangled pair to visualize</p>
        </div>
    `;
}

// Initialize Compression Lab
function initializeCompressionLab() {
    // Initial compression visualization placeholder
    document.getElementById('compression-visualization').innerHTML = `
        <div class="text-center py-3">
            <p class="text-muted">Compression mapping visualization will appear here</p>
        </div>
    `;
}

// Initialize Demos
function initializeDemos() {
    // Nothing specific to initialize for demos yet
}

// Create Initial Objects
async function createInitialObjects() {
    try {
        // Create initial grid
        const gridResponse = await fetch(`${API_BASE_URL}/grids`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ size: 100 })
        });
        
        if (gridResponse.ok) {
            const gridData = await gridResponse.json();
            appState.grid.currentGridId = gridData.id;
            appState.grid.grids[gridData.id] = gridData;
            
            // Update grid info display
            updateGridInfo(gridData);
            
            // Load grid visualization
            updateGridView();
        }
        
        // Create initial observer
        const observerResponse = await fetch(`${API_BASE_URL}/observers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                name: 'Default Observer',
                focus_layers: [0]
            })
        });
        
        if (observerResponse.ok) {
            const observerData = await observerResponse.json();
            appState.observer.currentObserverId = observerData.id;
            appState.observer.observers[observerData.id] = observerData;
            
            // Update observer list
            updateObserverList();
        }
        
        // Create initial frequency processor
        const processorResponse = await fetch(`${API_BASE_URL}/frequency`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (processorResponse.ok) {
            const processorData = await processorResponse.json();
            appState.frequency.currentProcessorId = processorData.id;
            appState.frequency.processors[processorData.id] = processorData;
        }
        
        // Create initial compression database
        const dbResponse = await fetch(`${API_BASE_URL}/compression`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ grid_size: 100 })
        });
        
        if (dbResponse.ok) {
            const dbData = await dbResponse.json();
            appState.compression.currentDbId = dbData.id;
            appState.compression.dbs[dbData.id] = dbData;
            
            // Update compression DB stats
            updateCompressionStats(dbData);
        }
    } catch (error) {
        console.error('Error creating initial objects:', error);
        showErrorMessage('Failed to initialize application. Please check if the backend server is running.');
    }
}

// Grid Operations
async function createGrid(size) {
    try {
        const response = await fetch(`${API_BASE_URL}/grids`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ size })
        });
        
        if (response.ok) {
            const gridData = await response.json();
            appState.grid.currentGridId = gridData.id;
            appState.grid.grids[gridData.id] = gridData;
            
            // Update grid info display
            updateGridInfo(gridData);
            
            // Load grid visualization
            updateGridView();
            
            showSuccessMessage(`Created new grid with ID: ${gridData.id}`);
        } else {
            const errorData = await response.json();
            showErrorMessage(`Failed to create grid: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error creating grid:', error);
        showErrorMessage('Failed to create grid. Please check if the backend server is running.');
    }
}

async function updateGridView() {
    if (!appState.grid.currentGridId) {
        showErrorMessage('No grid selected. Please create or load a grid first.');
        return;
    }
    
    // Update view settings from inputs
    appState.grid.viewSettings.startRow = parseInt(document.getElementById('view-start-row').value);
    appState.grid.viewSettings.startCol = parseInt(document.getElementById('view-start-col').value);
    appState.grid.viewSettings.rows = parseInt(document.getElementById('view-rows').value);
    appState.grid.viewSettings.cols = parseInt(document.getElementById('view-cols').value);
    
    // Update effects settings if enabled
    if (appState.grid.effects.lightning.enabled) {
        appState.grid.effects.lightning.row = parseInt(document.getElementById('lightning-row').value);
        appState.grid.effects.lightning.col = parseInt(document.getElementById('lightning-col').value);
    }
    
    if (appState.grid.effects.whirlwind.enabled) {
        appState.grid.effects.whirlwind.row = parseInt(document.getElementById('whirlwind-row').value);
        appState.grid.effects.whirlwind.col = parseInt(document.getElementById('whirlwind-col').value);
        appState.grid.effects.whirlwind.intensity = parseFloat(document.getElementById('whirlwind-intensity').value);
    }
    
    // Update current view range display
    document.getElementById('current-view-range').textContent = 
        `[${appState.grid.viewSettings.startRow}:${appState.grid.viewSettings.startRow + appState.grid.viewSettings.rows}, ` +
        `${appState.grid.viewSettings.startCol}:${appState.grid.viewSettings.startCol + appState.grid.viewSettings.cols}]`;
    
    try {
        // Construct URL with parameters
        let url = `${API_BASE_URL}/grids/${appState.grid.currentGridId}/visualize?` +
            `start_row=${appState.grid.viewSettings.startRow}&` +
            `start_col=${appState.grid.viewSettings.startCol}&` +
            `rows=${appState.grid.viewSettings.rows}&` +
            `cols=${appState.grid.viewSettings.cols}`;
        
        // Add lightning effect if enabled
        if (appState.grid.effects.lightning.enabled) {
            url += `&lightning_row=${appState.grid.effects.lightning.row}&` +
                   `lightning_col=${appState.grid.effects.lightning.col}`;
        }
        
        // Add whirlwind effect if enabled
        if (appState.grid.effects.whirlwind.enabled) {
            url += `&whirlwind_row=${appState.grid.effects.whirlwind.row}&` +
                   `whirlwind_col=${appState.grid.effects.whirlwind.col}&` +
                   `whirlwind_intensity=${appState.grid.effects.whirlwind.intensity}`;
        }
        
        const response = await fetch(url);
        
        if (response.ok) {
            const data = await response.json();
            
            // Display the grid visualization
            document.getElementById('grid-visualization').innerHTML = `
                <img src="data:image/png;base64,${data.image}" class="img-fluid" alt="Grid Visualization">
            `;
            
            // Add click handler to the image for cell selection
            const img = document.getElementById('grid-visualization').querySelector('img');
            img.addEventListener('click', handleGridImageClick);
        } else {
            const errorData = await response.json();
            showErrorMessage(`Failed to update grid view: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error updating grid view:', error);
        showErrorMessage('Failed to update grid view. Please check if the backend server is running.');
    }
}

function updateGridInfo(gridData) {
    document.getElementById('current-grid-id').textContent = gridData.id;
    document.getElementById('current-grid-size').textContent = `${gridData.size}x${gridData.size}`;
}

function handleGridImageClick(event) {
    // This is a simplified implementation
    // In a real implementation, you would calculate the actual grid coordinates based on the click position
    
    // For now, we'll just show a modal with some sample cell information
    const modal = new bootstrap.Modal(document.getElementById('cell-detail-modal'));
    
    // Set sample values
    document.getElementById('detail-position').textContent = '[5, 5]';
    document.getElementById('detail-value').textContent = '8';
    document.getElementById('detail-is-origin').textContent = 'No';
    
    // Sample lineage tree
    document.getElementById('lineage-tree').innerHTML = `
        <div class="lineage-node">
            <div class="node-value">8</div>
            <div class="node-position">[5, 5]</div>
            <div class="node-children">
                <div class="lineage-node">
                    <div class="node-value">3</div>
                    <div class="node-position">[4, 5]</div>
                </div>
                <div class="lineage-node">
                    <div class="node-value">5</div>
                    <div class="node-position">[5, 4]</div>
                </div>
            </div>
        </div>
    `;
    
    // Sample lightning visualization
    document.getElementById('lightning-visualization').innerHTML = `
        <div class="text-center">
            <p class="text-muted">Lightning path visualization would appear here</p>
        </div>
    `;
    
    modal.show();
}

// Observer Operations
async function createObserver(name, focusLayers, transformationMatrix) {
    try {
        const requestBody = {
            name,
            focus_layers: focusLayers
        };
        
        if (transformationMatrix) {
            requestBody.transformation_matrix = transformationMatrix;
        }
        
        const response = await fetch(`${API_BASE_URL}/observers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (response.ok) {
            const observerData = await response.json();
            appState.observer.currentObserverId = observerData.id;
            appState.observer.observers[observerData.id] = observerData;
            
            // Update observer list
            updateObserverList();
            
            showSuccessMessage(`Created new observer: ${name}`);
        } else {
            const errorData = await response.json();
            showErrorMessage(`Failed to create observer: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error creating observer:', error);
        showErrorMessage('Failed to create observer. Please check if the backend server is running.');
    }
}

function updateObserverList() {
    const observerList = document.getElementById('observer-list');
    if (!observerList) return;
    
    observerList.innerHTML = '';
    
    Object.values(appState.observer.observers).forEach(observer => {
        const isActive = observer.id === appState.observer.currentObserverId;
        
        const listItem = document.createElement('a');
        listItem.href = '#';
        listItem.className = `list-group-item list-group-item-action d-flex justify-content-between align-items-center ${isActive ? 'active' : ''}`;
        listItem.textContent = observer.name;
        
        if (isActive) {
            const badge = document.createElement('span');
            badge.className = 'badge bg-primary rounded-pill';
            badge.textContent = 'Active';
            listItem.appendChild(badge);
        }
        
        listItem.addEventListener('click', (e) => {
            e.preventDefault();
            appState.observer.currentObserverId = observer.id;
            updateObserverList();
        });
        
        observerList.appendChild(listItem);
    });
}

function updateTransformationMatrixDisplay() {
    const matrixElement = document.getElementById('transformation-matrix');
    if (!matrixElement) return;
    
    matrixElement.innerHTML = '';
    
    for (let i = 0; i < 10; i++) {
        const row = document.createElement('tr');
        
        const labelCell = document.createElement('td');
        labelCell.className = 'matrix-label';
        labelCell.textContent = `${i + 1} →`;
        row.appendChild(labelCell);
        
        const valueCell = document.createElement('td');
        const input = document.createElement('input');
        input.type = 'number';
        input.className = 'form-control form-control-sm';
        input.value = appState.observer.transformationMatrix[i][0];
        input.min = 1;
        input.max = 10;
        input.dataset.row = i;
        input.dataset.col = 0;
        
        input.addEventListener('change', (e) => {
            const row = parseInt(e.target.dataset.row);
            const col = parseInt(e.target.dataset.col);
            const value = parseInt(e.target.value);
            
            if (value < 1 || value > 10) {
                e.target.value = appState.observer.transformationMatrix[row][col];
                return;
            }
            
            appState.observer.transformationMatrix[row][col] = value;
        });
        
        valueCell.appendChild(input);
        row.appendChild(valueCell);
        
        matrixElement.appendChild(row);
    }
}

function createIdentityMatrix() {
    const matrix = Array(10).fill().map(() => Array(1).fill(0));
    
    for (let i = 0; i < 10; i++) {
        matrix[i][0] = i + 1;
    }
    
    return matrix;
}

function createShiftMatrix(shift) {
    const matrix = Array(10).fill().map(() => Array(1).fill(0));
    
    for (let i = 0; i < 10; i++) {
        matrix[i][0] = ((i + shift) % 10) + 1;
    }
    
    return matrix;
}

function createInvertMatrix() {
    const matrix = Array(10).fill().map(() => Array(1).fill(0));
    
    for (let i = 0; i < 10; i++) {
        matrix[i][0] = 10 - i;
    }
    
    return matrix;
}

function populateGridSelector() {
    const gridSelector = document.getElementById('grid-selector');
    if (!gridSelector) return;
    
    gridSelector.innerHTML = '<option value="">Select a grid...</option>';
    
    Object.values(appState.grid.grids).forEach(grid => {
        const option = document.createElement('option');
        option.value = grid.id;
        option.textContent = `Grid ${grid.id} (${grid.size}x${grid.size})`;
        
        if (grid.id === appState.grid.currentGridId) {
            option.selected = true;
        }
        
        gridSelector.appendChild(option);
    });
    
    gridSelector.addEventListener('change', () => {
        const selectedGridId = gridSelector.value;
        if (selectedGridId && appState.observer.currentObserverId) {
            observeGrid(appState.observer.currentObserverId, selectedGridId);
        }
    });
}

async function observeGrid(observerId, gridId) {
    try {
        const response = await fetch(`${API_BASE_URL}/observers/${observerId}/observe/${gridId}`);
        
        if (response.ok) {
            const data = await response.json();
            
            // For now, just show a placeholder
            document.getElementById('observer-visualization').innerHTML = `
                <div class="text-center py-3">
                    <p>Observer ${observerId} is observing Grid ${gridId}</p>
                    <p>The observed grid has dimensions: ${data.observed_grid.length}x${data.observed_grid[0].length}</p>
                </div>
            `;
            
            // In a real implementation, you would visualize the observed grid
        } else {
            const errorData = await response.json();
            showErrorMessage(`Failed to observe grid: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error observing grid:', error);
        showErrorMessage('Failed to observe grid. Please check if the backend server is running.');
    }
}

// Frequency Operations
async function generateBeatPattern() {
    if (!appState.frequency.currentProcessorId) {
        showErrorMessage('No frequency processor selected. Please create or load a processor first.');
        return;
    }
    
    const freq1 = parseFloat(document.getElementById('frequency1').value);
    const freq2 = parseFloat(document.getElementById('frequency2').value);
    const duration = parseFloat(document.getElementById('duration').value);
    
    try {
        const response = await fetch(`${API_BASE_URL}/frequency/${appState.frequency.currentProcessorId}/beat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                freq1,
                freq2,
                duration,
                sample_rate: 1000
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Display the beat pattern visualization
            document.getElementById('frequency-visualization').innerHTML = `
                <img src="data:image/png;base64,${data.image}" class="img-fluid" alt="Beat Pattern Visualization">
            `;
            
            // Add to timeline
            addToFrequencyTimeline('Beat Pattern', `${freq1} Hz + ${freq2} Hz`, `${data.pattern.beat_frequency} Hz beat`);
            
            showSuccessMessage(`Generated beat pattern: ${freq1} Hz + ${freq2} Hz = ${data.pattern.beat_frequency} Hz beat`);
        } else {
            const errorData = await response.json();
            showErrorMessage(`Failed to generate beat pattern: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error generating beat pattern:', error);
        showErrorMessage('Failed to generate beat pattern. Please check if the backend server is running.');
    }
}

function addToFrequencyTimeline(type, original, result) {
    const timelineEntries = document.getElementById('timeline-entries');
    if (!timelineEntries) return;
    
    // Clear "no entries" message if present
    if (timelineEntries.querySelector('td[colspan="5"]')) {
        timelineEntries.innerHTML = '';
    }
    
    const now = new Date();
    const timestamp = now.toLocaleTimeString();
    
    const row = document.createElement('tr');
    
    const timestampCell = document.createElement('td');
    timestampCell.textContent = timestamp;
    row.appendChild(timestampCell);
    
    const typeCell = document.createElement('td');
    typeCell.textContent = type;
    row.appendChild(typeCell);
    
    const originalCell = document.createElement('td');
    originalCell.textContent = original;
    row.appendChild(originalCell);
    
    const resultCell = document.createElement('td');
    resultCell.textContent = result;
    row.appendChild(resultCell);
    
    const actionsCell = document.createElement('td');
    const viewBtn = document.createElement('button');
    viewBtn.className = 'btn btn-sm btn-outline-primary';
    viewBtn.innerHTML = '<i class="bi bi-eye"></i>';
    viewBtn.addEventListener('click', () => {
        // In a real implementation, this would show details
        alert(`Details for ${type}: ${original} → ${result}`);
    });
    actionsCell.appendChild(viewBtn);
    row.appendChild(actionsCell);
    
    timelineEntries.prepend(row);
    
    // Store in app state
    appState.frequency.timeline.unshift({
        timestamp,
        type,
        original,
        result
    });
}

// Compression Operations
async function compressData() {
    if (!appState.compression.currentDbId) {
        showErrorMessage('No compression database selected. Please create or load a database first.');
        return;
    }
    
    const inputText = document.getElementById('compression-input').value;
    if (!inputText) {
        showErrorMessage('Please enter text to compress.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/compression/${appState.compression.currentDbId}/compress`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: inputText
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Store the compressed data
            appState.compression.lastCompressed = data.compressed;
            
            // Update the hash and compressed data inputs for decompression
            document.getElementById('hash-input').value = data.compressed.hash;
            document.getElementById('compressed-data-input').value = data.compressed.compressed_data;
            
            // Display compression results
            document.getElementById('original-size').textContent = data.compressed.original_size;
            document.getElementById('compressed-size').textContent = data.compressed.compressed_size;
            document.getElementById('compression-ratio').textContent = data.compressed.compression_ratio.toFixed(2);
            document.getElementById('compression-time').textContent = (data.compressed.execution_time * 1000).toFixed(2);
            
            document.getElementById('compression-result').style.display = 'block';
            
            // Update DB stats
            updateCompressionStats(appState.compression.dbs[appState.compression.currentDbId]);
            
            showSuccessMessage(`Compressed data: ${data.compressed.original_size} bytes → ${data.compressed.compressed_size} bytes (${data.compressed.compression_ratio.toFixed(2)}x)`);
        } else {
            const errorData = await response.json();
            showErrorMessage(`Failed to compress data: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error compressing data:', error);
        showErrorMessage('Failed to compress data. Please check if the backend server is running.');
    }
}

async function decompressData() {
    if (!appState.compression.currentDbId) {
        showErrorMessage('No compression database selected. Please create or load a database first.');
        return;
    }
    
    const hash = document.getElementById('hash-input').value;
    const compressedData = document.getElementById('compressed-data-input').value;
    
    if (!hash || !compressedData) {
        showErrorMessage('Please enter hash and compressed data.');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/compression/${appState.compression.currentDbId}/decompress`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                compressed: {
                    hash,
                    compressed_data: compressedData
                }
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Store the decompressed data
            appState.compression.lastDecompressed = data.decompressed;
            
            // Display decompression results
            document.getElementById('decompression-time').textContent = (data.decompressed.execution_time * 1000).toFixed(2);
            document.getElementById('decompressed-output').value = data.decompressed.data;
            
            document.getElementById('decompression-result').style.display = 'block';
            
            showSuccessMessage(`Decompressed data: ${data.decompressed.original_size} bytes`);
        } else {
            const errorData = await response.json();
            showErrorMessage(`Failed to decompress data: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error decompressing data:', error);
        showErrorMessage('Failed to decompress data. Please check if the backend server is running.');
    }
}

function updateCompressionStats(dbData) {
    document.getElementById('db-id').textContent = dbData.id;
    document.getElementById('total-compressed').textContent = dbData.stats.total_compressed;
    document.getElementById('total-original-size').textContent = dbData.stats.total_original_size;
    document.getElementById('total-compressed-size').textContent = dbData.stats.total_compressed_size;
    document.getElementById('overall-ratio').textContent = dbData.stats.compression_ratio.toFixed(2);
}

function loadSampleText() {
    const sampleType = document.getElementById('sample-text').value;
    let sampleText = '';
    
    switch (sampleType) {
        case 'lorem':
            sampleText = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies aliquam, nunc nisl aliquet nunc, vitae aliquam nisl nunc vitae nisl. Nullam auctor, nisl eget ultricies aliquam, nunc nisl aliquet nunc, vitae aliquam nisl nunc vitae nisl. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies aliquam, nunc nisl aliquet nunc, vitae aliquam nisl nunc vitae nisl.';
            break;
        case 'code':
            sampleText = `function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

for (let i = 0; i < 10; i++) {
    console.log(fibonacci(i));
}`;
            break;
        case 'json':
            sampleText = `{
    "name": "Fibonacci Grid System",
    "version": "1.0.0",
    "description": "A system for grid-based data processing",
    "features": [
        "Grid generation",
        "Observer perspectives",
        "Frequency analysis",
        "Data compression"
    ],
    "settings": {
        "gridSize": 100,
        "defaultObserver": "DefaultObserver",
        "compressionEnabled": true
    }
}`;
            break;
        default:
            return;
    }
    
    document.getElementById('compression-input').value = sampleText;
}

// Demo Operations
function launchDemo(demoType) {
    const modal = new bootstrap.Modal(document.getElementById('demo-modal'));
    const demoTitle = document.getElementById('demo-title');
    const demoContent = document.getElementById('demo-content');
    
    // Set demo title
    switch (demoType) {
        case 'messaging':
            demoTitle.textContent = 'Secure Messaging Demo';
            break;
        case 'memory':
            demoTitle.textContent = 'Memory System Demo';
            break;
        case 'pattern':
            demoTitle.textContent = 'Pattern Recognition Demo';
            break;
        case 'compression':
            demoTitle.textContent = 'Data Compression Demo';
            break;
        case 'network':
            demoTitle.textContent = 'Network Transfer Demo';
            break;
        case 'ai':
            demoTitle.textContent = 'AI Enhancement Demo';
            break;
        default:
            demoTitle.textContent = 'Demo';
    }
    
    // Set demo content (placeholder for now)
    demoContent.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading ${demoType} demo...</p>
        </div>
    `;
    
    modal.show();
    
    // Simulate loading demo content
    setTimeout(() => {
        demoContent.innerHTML = `
            <div class="alert alert-info">
                <p>This is a placeholder for the ${demoType} demo. In a complete implementation, this would contain an interactive demonstration.</p>
            </div>
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-light">
                            <h6 class="mb-0">Demo Controls</h6>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <button class="btn btn-primary">Start Demo</button>
                                <button class="btn btn-secondary">Reset</button>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Demo Speed</label>
                                <input type="range" class="form-range" min="0.5" max="2" step="0.1" value="1">
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-light">
                            <h6 class="mb-0">Demo Output</h6>
                        </div>
                        <div class="card-body">
                            <p>Demo output will appear here when the demo is started.</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }, 1500);
}

// Utility Functions
function showSuccessMessage(message) {
    // In a real implementation, this would show a toast or notification
    console.log('Success:', message);
    
    // Create a toast notification
    const toastContainer = document.createElement('div');
    toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '5';
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const toastHeader = document.createElement('div');
    toastHeader.className = 'toast-header bg-success text-white';
    
    const toastTitle = document.createElement('strong');
    toastTitle.className = 'me-auto';
    toastTitle.textContent = 'Success';
    
    const toastClose = document.createElement('button');
    toastClose.type = 'button';
    toastClose.className = 'btn-close btn-close-white';
    toastClose.setAttribute('data-bs-dismiss', 'toast');
    toastClose.setAttribute('aria-label', 'Close');
    
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body';
    toastBody.textContent = message;
    
    toastHeader.appendChild(toastTitle);
    toastHeader.appendChild(toastClose);
    
    toast.appendChild(toastHeader);
    toast.appendChild(toastBody);
    
    toastContainer.appendChild(toast);
    document.body.appendChild(toastContainer);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove the toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toastContainer);
    });
}

function showErrorMessage(message) {
    // In a real implementation, this would show a toast or notification
    console.error('Error:', message);
    
    // Create a toast notification
    const toastContainer = document.createElement('div');
    toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
    toastContainer.style.zIndex = '5';
    
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    const toastHeader = document.createElement('div');
    toastHeader.className = 'toast-header bg-danger text-white';
    
    const toastTitle = document.createElement('strong');
    toastTitle.className = 'me-auto';
    toastTitle.textContent = 'Error';
    
    const toastClose = document.createElement('button');
    toastClose.type = 'button';
    toastClose.className = 'btn-close btn-close-white';
    toastClose.setAttribute('data-bs-dismiss', 'toast');
    toastClose.setAttribute('aria-label', 'Close');
    
    const toastBody = document.createElement('div');
    toastBody.className = 'toast-body';
    toastBody.textContent = message;
    
    toastHeader.appendChild(toastTitle);
    toastHeader.appendChild(toastClose);
    
    toast.appendChild(toastHeader);
    toast.appendChild(toastBody);
    
    toastContainer.appendChild(toast);
    document.body.appendChild(toastContainer);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove the toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        document.body.removeChild(toastContainer);
    });
}
