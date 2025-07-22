import axios from 'axios';

// Update the base URL to point to our Flask backend
const API_BASE_URL = 'http://localhost:5000/api/search-wizard';

export interface Product {
  id: string;
  title: string;
  price: number;
  original_price?: number;
  discount?: number;
  url: string;
  image_url: string;
  category: string;
  brand?: string;
  in_stock: boolean;
  last_updated: string;
}

export interface SearchResult {
  id: string;
  search_name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  products: Product[];
  created_at: string;
  updated_at: string;
  error?: string;
}

/**
 * Start a new product search
 */
export const startProductSearch = async (options: {
  searchName: string;
  productQuery: string;
  category?: string;
  minPriceUsd?: number;
  maxPriceUsd?: number;
  saveImages?: boolean;
}) => {
  try {
    const response = await axios.post<{ search_id: string }>(
      `${API_BASE_URL}/wizard/step1`,
      {
        search_name: options.searchName,
        product_query: options.productQuery,
        category: options.category,
        min_price_usd: options.minPriceUsd,
        max_price_usd: options.maxPriceUsd,
        save_images: options.saveImages,
      }
    );
    
    // Start the search immediately
    await axios.post(`${API_BASE_URL}/wizard/step2/test`, {
      search_id: response.data.search_id
    });
    
    return response.data.search_id;
  } catch (error) {
    console.error('Error starting product search:', error);
    throw error;
  }
};

/**
 * Check the status of a search
 */
export const checkSearchStatus = async (searchId: string): Promise<SearchResult> => {
  try {
    const response = await axios.get<SearchResult>(`${API_BASE_URL}/search/${searchId}`);
    return response.data;
  } catch (error) {
    console.error('Error checking search status:', error);
    throw error;
  }
};

/**
 * Get products from a completed search
 */
export const getSearchProducts = async (searchId: string): Promise<Product[]> => {
  try {
    const response = await axios.get<{ products: Product[] }>(
      `${API_BASE_URL}/search/${searchId}/products`
    );
    return response.data.products;
  } catch (error) {
    console.error('Error getting search products:', error);
    throw error;
  }
};

/**
 * Get all saved searches
 */
export const getSavedSearches = async (): Promise<SearchResult[]> => {
  try {
    const response = await axios.get<{ searches: SearchResult[] }>(
      `${API_BASE_URL}/searches`
    );
    return response.data.searches;
  } catch (error) {
    console.error('Error getting saved searches:', error);
    throw error;
  }
};

/**
 * Toggle search status (active/inactive)
 */
export const toggleSearchStatus = async (searchId: string): Promise<boolean> => {
  try {
    const response = await axios.post<{ success: boolean }>(
      `${API_BASE_URL}/search/${searchId}/toggle`
    );
    return response.data.success;
  } catch (error) {
    console.error('Error toggling search status:', error);
    throw error;
  }
};
