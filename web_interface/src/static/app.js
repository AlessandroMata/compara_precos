// Paraguai Price Extractor - Frontend JavaScript

// Global variables
let currentUser = null;
let currentSearchConfig = null;
let testResults = [];
let selectedProducts = [];

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
});

// Authentication functions
async function checkAuthentication() {
    try {
        const response = await fetch('/api/auth/check');
        const data = await response.json();
        
        if (data.authenticated) {
            currentUser = data.user;
            showMainApp();
        } else {
            showLoginModal();
        }
    } catch (error) {
        console.error('Auth check error:', error);
        showLoginModal();
    }
}

function showLoginModal() {
    document.getElementById('mainApp').classList.add('d-none');
    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
}

function showMainApp() {
    document.getElementById('mainApp').classList.remove('d-none');
    document.getElementById('userDisplay').textContent = currentUser.username;
    
    // Close login modal if open
    const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
    if (loginModal) {
        loginModal.hide();
    }
    
    // Load initial data
    loadSavedSearches();
}

// Login form handler
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = data.user;
            showMainApp();
            document.getElementById('loginForm').reset();
            hideError('loginError');
        } else {
            showError('loginError', data.error || 'Erro no login');
        }
    } catch (error) {
        showError('loginError', 'Erro de conexão');
    } finally {
        showLoading(false);
    }
});

async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        currentUser = null;
        showLoginModal();
    } catch (error) {
        console.error('Logout error:', error);
    }
}

// Wizard functions
async function testSearch() {
    const config = getWizardConfig();
    if (!config) return;
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/search-wizard/step2/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ config })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSearchConfig = config;
            testResults = data.products;
            displayTestResults(data.products, data.stats);
            document.getElementById('approveBtn').classList.remove('d-none');
        } else {
            showAlert('Erro no teste: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão', 'danger');
    } finally {
        showLoading(false);
    }
}

async function approveSearch() {
    if (!currentSearchConfig || selectedProducts.length === 0) {
        showAlert('Selecione pelo menos um produto para aprovar', 'warning');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/search-wizard/step3/approve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                config: currentSearchConfig,
                approved_products: selectedProducts
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Busca aprovada e salva com sucesso!', 'success');
            resetWizard();
            loadSavedSearches();
        } else {
            showAlert('Erro ao aprovar: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão', 'danger');
    } finally {
        showLoading(false);
    }
}

function getWizardConfig() {
    const searchName = document.getElementById('searchName').value.trim();
    const productQuery = document.getElementById('productQuery').value.trim();
    
    if (!searchName || !productQuery) {
        showAlert('Preencha nome da busca e produto', 'warning');
        return null;
    }
    
    return {
        search_name: searchName,
        product_query: productQuery,
        min_price_usd: parseFloat(document.getElementById('minPrice').value) || null,
        max_price_usd: parseFloat(document.getElementById('maxPrice').value) || null,
        sort_by: document.getElementById('sortBy').value,
        in_stock_only: document.getElementById('inStockOnly').checked
    };
}

function displayTestResults(products, stats) {
    const resultsDiv = document.getElementById('testResults');
    const productsList = document.getElementById('testProductsList');
    const statsDiv = document.getElementById('testStats');
    
    // Update stats
    statsDiv.innerHTML = `
        <div class="row text-center">
            <div class="col-6">
                <div class="stat-card">
                    <span class="stat-number">${stats.total_found}</span>
                    <span class="stat-label">Produtos Encontrados</span>
                </div>
            </div>
            <div class="col-6">
                <div class="stat-card">
                    <span class="stat-number">$${stats.price_range.min} - $${stats.price_range.max}</span>
                    <span class="stat-label">Faixa de Preço</span>
                </div>
            </div>
        </div>
        <div class="mt-3">
            <small><strong>Categorias:</strong> ${stats.categories.join(', ')}</small><br>
            <small><strong>Marcas:</strong> ${stats.brands.join(', ')}</small>
        </div>
    `;
    
    // Display products
    if (products.length === 0) {
        productsList.innerHTML = '<div class="text-center text-muted">Nenhum produto encontrado</div>';
    } else {
        productsList.innerHTML = products.map((product, index) => `
            <div class="search-result-item card p-3 mb-2" onclick="toggleProductSelection(${index})">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="product-title mb-2">${product.nome || 'Produto sem nome'}</h6>
                        <div class="d-flex gap-3 mb-2">
                            <span class="product-price">$${product.preco_usd || 'N/A'}</span>
                            <span class="text-muted">R$${product.preco_brl || 'N/A'}</span>
                            <span class="badge bg-secondary">${product.marca || 'N/A'}</span>
                        </div>
                        <small class="text-muted">${product.estoque || 'Status não informado'}</small>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="product_${index}">
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    resultsDiv.classList.remove('d-none');
    selectedProducts = [];
}

function toggleProductSelection(index) {
    const checkbox = document.getElementById(`product_${index}`);
    const productCard = checkbox.closest('.search-result-item');
    
    checkbox.checked = !checkbox.checked;
    
    if (checkbox.checked) {
        productCard.classList.add('selected');
        selectedProducts.push(testResults[index]);
    } else {
        productCard.classList.remove('selected');
        selectedProducts = selectedProducts.filter(p => p !== testResults[index]);
    }
}

function resetWizard() {
    document.getElementById('wizardForm').reset();
    document.getElementById('testResults').classList.add('d-none');
    document.getElementById('approveBtn').classList.add('d-none');
    document.getElementById('testStats').innerHTML = 'Execute um teste para ver as estatísticas';
    currentSearchConfig = null;
    testResults = [];
    selectedProducts = [];
}

// Saved searches functions
async function loadSavedSearches() {
    try {
        const response = await fetch('/api/search-wizard/searches');
        const data = await response.json();
        
        if (data.success) {
            displaySavedSearches(data.searches);
        }
    } catch (error) {
        console.error('Error loading searches:', error);
    }
}

function displaySavedSearches(searches) {
    const searchesList = document.getElementById('savedSearchesList');
    
    if (searches.length === 0) {
        searchesList.innerHTML = '<div class="text-center text-muted">Nenhuma busca salva</div>';
        return;
    }
    
    searchesList.innerHTML = searches.map(search => `
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="card-title">${search.name}</h5>
                        <p class="card-text">
                            <strong>Busca:</strong> ${search.query}<br>
                            <strong>Preço:</strong> $${search.min_price_usd || '0'} - $${search.max_price_usd || '∞'}<br>
                            <strong>Produtos:</strong> ${search.product_count}
                        </p>
                        <small class="text-muted">Criada em: ${new Date(search.created_at).toLocaleDateString('pt-BR')}</small>
                    </div>
                    <div class="d-flex flex-column gap-2">
                        <span class="badge ${search.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${search.is_active ? 'Ativa' : 'Inativa'}
                        </span>
                        <div class="btn-group-vertical btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="viewSearchProducts(${search.id})">
                                <i class="fas fa-eye"></i> Ver Produtos
                            </button>
                            <button class="btn btn-outline-secondary" onclick="toggleSearchStatus(${search.id})">
                                <i class="fas fa-toggle-${search.is_active ? 'on' : 'off'}"></i> 
                                ${search.is_active ? 'Desativar' : 'Ativar'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

async function viewSearchProducts(searchId) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/search-wizard/searches/${searchId}/products`);
        const data = await response.json();
        
        if (data.success) {
            // Switch to analysis tab and show products
            const analysisTab = new bootstrap.Tab(document.getElementById('analysis-tab'));
            analysisTab.show();
            
            displaySearchProducts(data.products, data.search_name);
        }
    } catch (error) {
        showAlert('Erro ao carregar produtos', 'danger');
    } finally {
        showLoading(false);
    }
}

function displaySearchProducts(products, searchName) {
    const analysisContent = document.getElementById('marketAnalysisContent');
    
    analysisContent.innerHTML = `
        <div class="mb-4">
            <h5><i class="fas fa-list me-2"></i>Produtos da busca: ${searchName}</h5>
        </div>
        <div class="row">
            ${products.map(product => {
                const productData = JSON.parse(product.product_data);
                return `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card product-card h-100" onclick="analyzeProduct(${product.saved_id})">
                            <div class="card-body">
                                <h6 class="product-title">${productData.nome || 'Produto'}</h6>
                                <div class="product-price mb-2">$${productData.preco_usd || 'N/A'}</div>
                                <div class="text-muted mb-2">R$${productData.preco_brl || 'N/A'}</div>
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="badge bg-primary">${productData.marca || 'N/A'}</span>
                                    <button class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-chart-bar"></i> Analisar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

async function toggleSearchStatus(searchId) {
    try {
        const response = await fetch(`/api/search-wizard/searches/${searchId}/toggle`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            loadSavedSearches();
        }
    } catch (error) {
        showAlert('Erro ao alterar status', 'danger');
    }
}

// Opportunities functions
async function findOpportunities() {
    try {
        showLoading(true);
        
        const response = await fetch('/api/search-wizard/opportunities', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                max_price_usd: 500,
                min_opportunity_score: 7.0
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayOpportunities(data.opportunities);
        }
    } catch (error) {
        showAlert('Erro ao buscar oportunidades', 'danger');
    } finally {
        showLoading(false);
    }
}

function displayOpportunities(opportunities) {
    const opportunitiesList = document.getElementById('opportunitiesList');
    
    if (opportunities.length === 0) {
        opportunitiesList.innerHTML = '<div class="text-center text-muted">Nenhuma oportunidade encontrada</div>';
        return;
    }
    
    opportunitiesList.innerHTML = opportunities.map(opp => `
        <div class="card mb-3 fade-in-up">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1">
                        <h6 class="card-title">${opp.product.nome || 'Produto'}</h6>
                        <div class="d-flex gap-3 mb-2">
                            <span class="product-price">$${opp.product.preco_usd}</span>
                            <span class="badge position-${opp.market_position}">${opp.market_position}</span>
                            <span class="opportunity-score score-${opp.value_rating}">
                                Score: ${opp.opportunity_score.toFixed(1)}/10
                            </span>
                        </div>
                        <div class="recommendations">
                            ${opp.recommendations.map(rec => `
                                <div class="recommendation-item recommendation-${opp.value_rating}">
                                    ${rec}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-primary" onclick="analyzeProductFromUrl('${opp.product.url}')">
                            <i class="fas fa-chart-line"></i> Analisar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// Market analysis functions
async function analyzeProduct(productId) {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/market-analysis/product/${productId}`);
        const data = await response.json();
        
        if (data.success) {
            displayMarketAnalysis(data.analysis);
        }
    } catch (error) {
        showAlert('Erro na análise de mercado', 'danger');
    } finally {
        showLoading(false);
    }
}

async function analyzeProductFromUrl(url) {
    try {
        showLoading(true);
        
        const response = await fetch('/api/market-analysis/url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayMarketAnalysis(data.analysis);
            
            // Switch to analysis tab
            const analysisTab = new bootstrap.Tab(document.getElementById('analysis-tab'));
            analysisTab.show();
        }
    } catch (error) {
        showAlert('Erro na análise de mercado', 'danger');
    } finally {
        showLoading(false);
    }
}

function displayMarketAnalysis(analysis) {
    const analysisContent = document.getElementById('marketAnalysisContent');
    
    analysisContent.innerHTML = `
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-bar me-2"></i>Análise de Mercado</h5>
                    </div>
                    <div class="card-body">
                        <h6>${analysis.product_name}</h6>
                        
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <h6>Preços de Mercado</h6>
                                <div class="price-comparison">
                                    <span class="price-source">Mercado Oficial</span>
                                    <span class="price-value price-official">
                                        R$${analysis.official_min_price || 'N/A'} - R$${analysis.official_max_price || 'N/A'}
                                    </span>
                                </div>
                                <div class="price-comparison">
                                    <span class="price-source">Mercado Cinza</span>
                                    <span class="price-value price-gray">
                                        R$${analysis.gray_min_price || 'N/A'} - R$${analysis.gray_max_price || 'N/A'}
                                    </span>
                                </div>
                                <div class="price-comparison">
                                    <span class="price-source">Custo Total</span>
                                    <span class="price-value">R$${analysis.total_cost_estimate.toFixed(2)}</span>
                                </div>
                            </div>
                            
                            <div class="col-md-6">
                                <h6>Preços Sugeridos</h6>
                                ${Object.entries(analysis.suggested_prices).map(([type, price]) => `
                                    <div class="price-comparison">
                                        <span class="price-source">${type}</span>
                                        <span class="price-value price-suggested">R$${price.toFixed(2)}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <h6>Recomendações</h6>
                            ${analysis.recommendations.map(rec => `
                                <div class="recommendation-item recommendation-${analysis.opportunity_score >= 8 ? 'excellent' : analysis.opportunity_score >= 6 ? 'good' : 'warning'}">
                                    ${rec}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h6><i class="fas fa-trophy me-2"></i>Score de Oportunidade</h6>
                    </div>
                    <div class="card-body text-center">
                        <div class="opportunity-score score-${analysis.opportunity_score >= 8 ? 'excellent' : analysis.opportunity_score >= 6 ? 'good' : 'fair'} mb-3">
                            ${analysis.opportunity_score.toFixed(1)}/10
                        </div>
                        <div class="badge position-${analysis.market_position} mb-3">
                            ${analysis.market_position}
                        </div>
                        <div class="exchange-rate">
                            1 USD = R$${analysis.exchange_rate || '5.50'}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Password change functions
function showChangePassword() {
    const modal = new bootstrap.Modal(document.getElementById('changePasswordModal'));
    modal.show();
}

async function changePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    if (newPassword !== confirmPassword) {
        showError('passwordError', 'Senhas não coincidem');
        return;
    }
    
    if (newPassword.length < 6) {
        showError('passwordError', 'Nova senha deve ter pelo menos 6 caracteres');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Senha alterada com sucesso!', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('changePasswordModal'));
            modal.hide();
            document.getElementById('changePasswordForm').reset();
            hideError('passwordError');
        } else {
            showError('passwordError', data.error);
        }
    } catch (error) {
        showError('passwordError', 'Erro de conexão');
    }
}

// Utility functions
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.remove('d-none');
    } else {
        overlay.classList.add('d-none');
    }
}

function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function showError(elementId, message) {
    const errorDiv = document.getElementById(elementId);
    errorDiv.textContent = message;
    errorDiv.classList.remove('d-none');
}

function hideError(elementId) {
    const errorDiv = document.getElementById(elementId);
    errorDiv.classList.add('d-none');
}

