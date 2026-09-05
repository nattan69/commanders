export type Table = {
  id: string;
  number: number;
  area: string;
  status: 'free' | 'occupied';
};

export type Area = {
  id: string;
  name: string;
};

export type Category = {
  id: string;
  name: string;
};

export type MenuItem = {
  id: string;
  category_id: string;
  name: string;
  price: number;
};

export type Order = {
  id: string;
  table_id: string;
  status: string;
  items: OrderItem[];
};

export type OrderItem = {
  id: string;
  item_id: string;
  quantity: number;
  price: number;
};

const API_BASE_URL = 'http://localhost:8000/api/v1';

// --- MOCKS ---
const MOCK_AREAS: Area[] = [
  { id: 'area-1', name: 'Terraza' },
  { id: 'area-2', name: 'Interior' },
  { id: 'area-3', name: 'Barra' },
];

const MOCK_TABLES: Table[] = [
  { id: 't1', number: 1, area: 'area-1', status: 'free' },
  { id: 't2', number: 2, area: 'area-1', status: 'occupied' },
  { id: 't3', number: 3, area: 'area-2', status: 'free' },
  { id: 't4', number: 4, area: 'area-2', status: 'occupied' },
  { id: 't5', number: 5, area: 'area-3', status: 'free' },
];

const MOCK_CATEGORIES: Category[] = [
  { id: 'cat-1', name: 'Begudes' },
  { id: 'cat-2', name: 'Tapes' },
  { id: 'cat-3', name: 'Postres' },
];

const MOCK_ITEMS: MenuItem[] = [
  { id: 'i1', category_id: 'cat-1', name: 'Coca-Cola', price: 2.5 },
  { id: 'i2', category_id: 'cat-1', name: 'Cervesa', price: 3.0 },
  { id: 'i3', category_id: 'cat-2', name: 'Patates', price: 6.0 },
  { id: 'i4', category_id: 'cat-2', name: 'Croquetas', price: 8.0 },
  { id: 'i5', category_id: 'cat-3', name: 'Flan', price: 4.0 },
];

async function apiRequest<T>(endpoint: string, options?: RequestInit, mockFallback?: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    if (!response.ok) throw new Error(`API error: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.warn(`API Request failed for ${endpoint}, using mock fallback:`, error);
    if (mockFallback !== undefined) return mockFallback;
    throw error;
  }
}

export const api = {
  async getTables(): Promise<Table[]> {
    return apiRequest('/tables', { method: 'GET' }, MOCK_TABLES);
  },
  async getAreas(): Promise<Area[]> {
    return apiRequest('/tables/areas', { method: 'GET' }, MOCK_AREAS);
  },
  async getCategories(): Promise<Category[]> {
    return apiRequest('/menu/categories', { method: 'GET' }, MOCK_CATEGORIES);
  },
  async getItems(): Promise<MenuItem[]> {
    return apiRequest('/menu/items', { method: 'GET' }, MOCK_ITEMS);
  },
  async createOrder(tableId: string, items: any[]): Promise<Order> {
    return apiRequest('/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ table_id: tableId, items }),
    }, { id: 'order-mock-1', table_id: tableId, status: 'open', items: [] });
  },
};
