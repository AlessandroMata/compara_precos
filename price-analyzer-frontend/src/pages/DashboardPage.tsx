import React, { useState, useEffect } from 'react';
import { 
  startProductSearch, 
  checkSearchStatus, 
  getSearchProducts,
  Product,
  SearchResult 
} from '../services/firecrawlService';
import {
  Box,
  Button,
  Card,
  CardContent,
  FormControl,
  FormControlLabel,
  InputLabel,
  LinearProgress,
  MenuItem,
  Paper,
  Select,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import Grid from '@mui/material/Grid';

const DashboardPage: React.FC = () => {
  const [category, setCategory] = useState<string>('eletronicos');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [maxProducts, setMaxProducts] = useState<number>(10);
  const [maxPriceUSD, setMaxPriceUSD] = useState<number>(1000);
  const [maxPriceBRL, setMaxPriceBRL] = useState<number>(5000);
  const [saveImages, setSaveImages] = useState<boolean>(true);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState<string | null>(null);

  const categories = [
    { value: 'eletronicos', label: 'Eletrônicos' },
    { value: 'celulares', label: 'Celulares' },
    { value: 'informatica', label: 'Informática' },
    { value: 'eletrodomesticos', label: 'Eletrodomésticos' },
    { value: 'perfumaria', label: 'Perfumaria' },
  ];

  const handleStartSearch = async () => {
    if (!searchTerm.trim()) {
      setError('Por favor, insira um termo de busca');
      return;
    }

    try {
      setIsSearching(true);
      setProgress(10);
      setError(null);

      // Start a new search
      const searchId = await startProductSearch({
        searchName: `Busca: ${searchTerm}`,
        productQuery: searchTerm,
        category: category,
        maxPriceUsd: maxPriceUSD,
        saveImages: saveImages
      });
      setProgress(30);

      // Poll for search completion
      const checkStatus = async () => {
        try {
          const statusResult = await checkSearchStatus(searchId);
          if (statusResult.status === 'completed') {
            setSearchResult(statusResult);
            const productsData = await getSearchProducts(searchId);
            setProducts(productsData);
            setProgress(100);
            setIsSearching(false);
          } else if (statusResult.status === 'failed') {
            setError(statusResult.error || 'Falha ao realizar a busca');
            setIsSearching(false);
          } else {
            // Still processing, check again in 2 seconds
            setTimeout(checkStatus, 2000);
            setProgress(prev => Math.min(prev + 10, 90)); // Gradually increase progress
          }
        } catch (err) {
          console.error('Error checking search status:', err);
          setError('Erro ao verificar status da busca');
          setIsSearching(false);
        }
      };

      // Start polling
      checkStatus();
    } catch (err) {
      console.error('Error starting search:', err);
      setError('Erro ao iniciar a busca');
      setIsSearching(false);
    }
    setSearchResult(null);
    setProducts([]);
  };

  

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Paraguai Price Analyzer
      </Typography>
      <Grid container spacing={3} component="div">
        <Grid  component="div">
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Configuração da Busca
            </Typography>
            <Grid container spacing={3} component="div">
              {/* Category */}
              <Grid  >
                <FormControl fullWidth>
                  <InputLabel id="category-label">Categoria</InputLabel>
                  <Select
                    labelId="category-label"
                    id="category"
                    value={category}
                    label="Categoria"
                    onChange={(e) => setCategory(e.target.value as string)}
                  >
                    {categories.map((cat) => (
                      <MenuItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              {/* Search Term */}
              <Grid   component="div">
                <TextField
                  fullWidth
                  label="Termo de Busca"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Ex: iPhone, Samsung, Perfume..."
                />
              </Grid>
              {/* Max Products */}
              <Grid    component="div">
                <FormControl fullWidth>
                  <InputLabel id="max-products-label">Máx. Produtos</InputLabel>
                  <Select
                    labelId="max-products-label"
                    id="max-products"
                    value={maxProducts}
                    label="Máx. Produtos"
                    onChange={(e) => setMaxProducts(Number(e.target.value))}
                  >
                    <MenuItem value={10}>10</MenuItem>
                    <MenuItem value={25}>25</MenuItem>
                    <MenuItem value={50}>50</MenuItem>
                    <MenuItem value={100}>100</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              {/* Max Price USD */}
              <Grid    component="div">
                <TextField
                  fullWidth
                  type="number"
                  label="Preço Máx. (USD)"
                  value={maxPriceUSD}
                  onChange={(e) => setMaxPriceUSD(Number(e.target.value))}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
              {/* Max Price BRL */}
              <Grid    component="div">
                <TextField
                  fullWidth
                  type="number"
                  label="Preço Máx. (BRL)"
                  value={maxPriceBRL}
                  onChange={(e) => setMaxPriceBRL(Number(e.target.value))}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
              {/* Save Images Toggle */}
              <Grid    component="div">
                <FormControlLabel
                  control={
                    <Switch
                      checked={saveImages}
                      onChange={(e) => setSaveImages(e.target.checked)}
                      color="primary"
                    />
                  }
                  label="Salvar Imagens"
                  labelPlacement="start"
                />
              </Grid>
            </Grid>
            {/* Search Button */}
            <Grid  sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Button
                variant="contained"
                color="primary"
                size="large"
                startIcon={<SearchIcon />}
                onClick={handleStartSearch}
              >
                Iniciar Busca
              </Button>
            </Grid>

              {searchResult?.status === 'completed' ? (
                <Box>
                  <Typography variant="subtitle1" gutterBottom>
                    Busca concluída! {products.length} itens encontrados.
                  </Typography>
                  <Grid container spacing={2} component="div">
                    {products.map((product, idx) => (
                      <Grid key={idx} component="div">
                        <Card>
                          <CardContent>
                            <Typography variant="subtitle1">{product.title || 'Sem nome'}</Typography>
                            <Typography variant="body2">Preço: {product.price}</Typography>
                            {/* Exibir outros dados do produto aqui */}
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              ) : isSearching ? (
                <Typography color="text.secondary" align="center" sx={{ mt: 2 }}>
                  Buscando produtos...
                </Typography>
              ) : (
                <Typography color="text.secondary" align="center" sx={{ mt: 4 }}>
                  Nenhum resultado encontrado. Clique em "Iniciar Busca" para começar.
                </Typography>
              )}
            </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
