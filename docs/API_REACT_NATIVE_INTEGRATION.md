# 📱 Documentação de Integração API Necessito - React Native

## 📋 Índice
- [Visão Geral](#visão-geral)
- [Configuração Inicial](#configuração-inicial)
- [Autenticação](#autenticação)
- [Estrutura da API](#estrutura-da-api)
- [Endpoints Principais](#endpoints-principais)
- [Casos de Uso Práticos](#casos-de-uso-práticos)
- [Tratamento de Erros](#tratamento-de-erros)
- [Boas Práticas](#boas-práticas)
- [Exemplos Completos](#exemplos-completos)

---

## 🎯 Visão Geral

A **API Necessito** é uma API RESTful construída com Django REST Framework que fornece acesso completo às funcionalidades do sistema. Esta documentação guiará a equipe de desenvolvimento mobile na integração com React Native.

### Características Principais
- **Base URL**: `https://necessito.online/api/`
- **Formato**: JSON
- **Autenticação**: Basic Auth / Session Auth
- **Documentação**: Disponível em `/api/swagger/` e `/api/redoc/`

### Recursos Disponíveis
- 👥 **Usuários** - Gerenciamento de clientes e fornecedores
- 📂 **Categorias** - Categorias e subcategorias de serviços
- 📢 **Necessidades** - Anúncios de clientes
- 💰 **Orçamentos** - Propostas de fornecedores
- ⭐ **Avaliações** - Sistema de reviews

---

## ⚙️ Configuração Inicial

### Instalação de Dependências

```bash
npm install axios react-native-async-storage
# ou
yarn add axios react-native-async-storage
```

### Configuração do Cliente HTTP

Crie um arquivo `src/services/api.js`:

```javascript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Configuração base da API
const API_BASE_URL = 'https://necessito.online/api/';

// Criação da instância do axios
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Interceptor para adicionar token de autenticação
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('auth_token');
    const username = await AsyncStorage.getItem('username');
    
    if (token && username) {
      // Basic Auth
      const credentials = btoa(`${username}:${token}`);
      config.headers.Authorization = `Basic ${credentials}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratamento de respostas
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      await AsyncStorage.multiRemove(['auth_token', 'username', 'user_data']);
      // Redirecionar para login
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 🔐 Autenticação

### Login do Usuário

```javascript
// src/services/authService.js
import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const authService = {
  // Login do usuário
  async login(email, password) {
    try {
      // Primeiro, fazer login via sessão Django
      const response = await api.post('auth/login/', {
        username: email,
        password: password,
      });
      
      // Salvar credenciais
      await AsyncStorage.setItem('username', email);
      await AsyncStorage.setItem('auth_token', password); // Para Basic Auth
      
      // Buscar dados do usuário
      const userResponse = await api.get('users/me/');
      await AsyncStorage.setItem('user_data', JSON.stringify(userResponse.data));
      
      return {
        success: true,
        user: userResponse.data,
      };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'Erro ao fazer login',
      };
    }
  },

  // Logout do usuário
  async logout() {
    try {
      await api.post('auth/logout/');
      await AsyncStorage.multiRemove(['auth_token', 'username', 'user_data']);
      return { success: true };
    } catch (error) {
      return { success: false, message: 'Erro ao fazer logout' };
    }
  },

  // Verificar se está logado
  async isAuthenticated() {
    try {
      const token = await AsyncStorage.getItem('auth_token');
      const username = await AsyncStorage.getItem('username');
      return !!(token && username);
    } catch {
      return false;
    }
  },

  // Obter dados do usuário atual
  async getCurrentUser() {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch {
      return null;
    }
  },
};
```

---

## 🏗️ Estrutura da API

### Endpoints Base

| Recurso | Endpoint | Descrição |
|---------|----------|-----------|
| Usuários | `/api/users/` | Gerenciamento de usuários |
| Categorias | `/api/categorias/` | Categorias de serviços |
| Subcategorias | `/api/subcategorias/` | Subcategorias específicas |
| Necessidades | `/api/necessidades/` | Anúncios de clientes |
| Orçamentos | `/api/orcamentos/` | Propostas de fornecedores |
| Avaliações | `/api/avaliacoes/` | Sistema de reviews |

### Estrutura de Resposta Padrão

```javascript
// Listagem (GET /api/necessidades/)
{
  "count": 150,
  "next": "https://necessito.online/api/necessidades/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "titulo": "Preciso de um eletricista",
      "descricao": "Instalação de tomadas...",
      // ... outros campos
    }
  ]
}

// Detalhes (GET /api/necessidades/1/)
{
  "id": 1,
  "titulo": "Preciso de um eletricista",
  "descricao": "Instalação de tomadas e interruptores",
  "cliente": {
    "id": 5,
    "first_name": "João",
    "last_name": "Silva"
  },
  // ... campos completos
}
```

---

## 📡 Endpoints Principais

### 👥 Usuários

```javascript
// src/services/userService.js
import api from './api';

export const userService = {
  // Listar usuários
  async getUsers(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`users/?${params}`);
    return response.data;
  },

  // Obter detalhes do usuário
  async getUserById(id) {
    const response = await api.get(`users/${id}/`);
    return response.data;
  },

  // Atualizar perfil
  async updateProfile(id, userData) {
    const response = await api.patch(`users/${id}/`, userData);
    return response.data;
  },

  // Obter avaliações do usuário
  async getUserReviews(id) {
    const response = await api.get(`users/${id}/avaliacoes/`);
    return response.data;
  },

  // Obter necessidades do usuário
  async getUserNeeds(id) {
    const response = await api.get(`users/${id}/necessidades/`);
    return response.data;
  },

  // Obter orçamentos do usuário
  async getUserBudgets(id) {
    const response = await api.get(`users/${id}/orcamentos/`);
    return response.data;
  },
};
```

### 📂 Categorias

```javascript
// src/services/categoryService.js
import api from './api';

export const categoryService = {
  // Listar todas as categorias
  async getCategories() {
    const response = await api.get('categorias/');
    return response.data.results;
  },

  // Obter detalhes da categoria
  async getCategoryById(id) {
    const response = await api.get(`categorias/${id}/`);
    return response.data;
  },

  // Obter subcategorias de uma categoria
  async getSubcategories(categoryId) {
    const response = await api.get(`categorias/${categoryId}/subcategorias/`);
    return response.data;
  },

  // Listar todas as subcategorias
  async getAllSubcategories(categoryId = null) {
    const params = categoryId ? `?categoria=${categoryId}` : '';
    const response = await api.get(`subcategorias/${params}`);
    return response.data.results;
  },
};
```

### 📢 Necessidades (Anúncios)

```javascript
// src/services/needService.js
import api from './api';

export const needService = {
  // Listar necessidades com filtros
  async getNeeds(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`necessidades/?${params}`);
    return response.data;
  },

  // Obter detalhes da necessidade
  async getNeedById(id) {
    const response = await api.get(`necessidades/${id}/`);
    return response.data;
  },

  // Criar nova necessidade
  async createNeed(needData) {
    const response = await api.post('necessidades/', needData);
    return response.data;
  },

  // Atualizar necessidade
  async updateNeed(id, needData) {
    const response = await api.patch(`necessidades/${id}/`, needData);
    return response.data;
  },

  // Deletar necessidade
  async deleteNeed(id) {
    await api.delete(`necessidades/${id}/`);
  },

  // Obter orçamentos da necessidade
  async getNeedBudgets(id) {
    const response = await api.get(`necessidades/${id}/orcamentos/`);
    return response.data;
  },

  // Upload de imagens
  async uploadImages(needId, images) {
    const formData = new FormData();
    images.forEach((image, index) => {
      formData.append(`image_${index}`, {
        uri: image.uri,
        type: image.type,
        name: image.name,
      });
    });

    const response = await api.post(
      `necessidades/${needId}/images/`, 
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};
```

### 💰 Orçamentos

```javascript
// src/services/budgetService.js
import api from './api';

export const budgetService = {
  // Listar orçamentos
  async getBudgets(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`orcamentos/?${params}`);
    return response.data;
  },

  // Criar novo orçamento
  async createBudget(budgetData) {
    const response = await api.post('orcamentos/', budgetData);
    return response.data;
  },

  // Atualizar orçamento
  async updateBudget(id, budgetData) {
    const response = await api.patch(`orcamentos/${id}/`, budgetData);
    return response.data;
  },

  // Aceitar orçamento
  async acceptBudget(id) {
    const response = await api.patch(`orcamentos/${id}/`, { 
      status: 'aceito' 
    });
    return response.data;
  },

  // Rejeitar orçamento
  async rejectBudget(id) {
    const response = await api.patch(`orcamentos/${id}/`, { 
      status: 'rejeitado' 
    });
    return response.data;
  },
};
```

### ⭐ Avaliações

```javascript
// src/services/reviewService.js
import api from './api';

export const reviewService = {
  // Criar avaliação
  async createReview(reviewData) {
    const response = await api.post('avaliacoes/', reviewData);
    return response.data;
  },

  // Listar avaliações
  async getReviews(filters = {}) {
    const params = new URLSearchParams(filters).toString();
    const response = await api.get(`avaliacoes/?${params}`);
    return response.data;
  },

  // Obter avaliações de um usuário
  async getUserReviews(userId) {
    const response = await api.get(`avaliacoes/?avaliado=${userId}`);
    return response.data;
  },
};
```

---

## 💡 Casos de Uso Práticos

### 📱 Tela de Login

```javascript
// src/screens/LoginScreen.js
import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, Text, Alert } from 'react-native';
import { authService } from '../services/authService';

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Erro', 'Preencha todos os campos');
      return;
    }

    setLoading(true);
    try {
      const result = await authService.login(email, password);
      
      if (result.success) {
        navigation.replace('Home');
      } else {
        Alert.alert('Erro', result.message);
      }
    } catch (error) {
      Alert.alert('Erro', 'Falha na conexão');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        style={{ borderWidth: 1, padding: 10, marginBottom: 10 }}
      />
      <TextInput
        placeholder="Senha"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={{ borderWidth: 1, padding: 10, marginBottom: 20 }}
      />
      <TouchableOpacity 
        onPress={handleLogin}
        disabled={loading}
        style={{ backgroundColor: '#007bff', padding: 15 }}
      >
        <Text style={{ color: 'white', textAlign: 'center' }}>
          {loading ? 'Entrando...' : 'Entrar'}
        </Text>
      </TouchableOpacity>
    </View>
  );
};

export default LoginScreen;
```

### 📋 Listagem de Necessidades

```javascript
// src/screens/NeedsScreen.js
import React, { useState, useEffect } from 'react';
import { 
  View, 
  FlatList, 
  Text, 
  TouchableOpacity, 
  RefreshControl 
} from 'react-native';
import { needService } from '../services/needService';

const NeedsScreen = ({ navigation }) => {
  const [needs, setNeeds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [filters, setFilters] = useState({
    status: 'ativo',
    page: 1,
  });

  const loadNeeds = async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
      setFilters(prev => ({ ...prev, page: 1 }));
    } else {
      setLoading(true);
    }

    try {
      const response = await needService.getNeeds(filters);
      
      if (isRefresh) {
        setNeeds(response.results);
      } else {
        setNeeds(prev => [...prev, ...response.results]);
      }
    } catch (error) {
      console.error('Erro ao carregar necessidades:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadNeeds();
  }, []);

  const renderNeedItem = ({ item }) => (
    <TouchableOpacity 
      style={{ 
        padding: 15, 
        borderBottomWidth: 1, 
        borderBottomColor: '#eee' 
      }}
      onPress={() => navigation.navigate('NeedDetail', { id: item.id })}
    >
      <Text style={{ fontSize: 16, fontWeight: 'bold' }}>
        {item.titulo}
      </Text>
      <Text style={{ color: '#666', marginTop: 5 }}>
        {item.descricao.substring(0, 100)}...
      </Text>
      <Text style={{ color: '#007bff', marginTop: 5 }}>
        {item.categoria_nome} • {item.cliente_nome}
      </Text>
    </TouchableOpacity>
  );

  return (
    <View style={{ flex: 1 }}>
      <FlatList
        data={needs}
        renderItem={renderNeedItem}
        keyExtractor={item => item.id.toString()}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={() => loadNeeds(true)}
          />
        }
        onEndReached={() => {
          setFilters(prev => ({ ...prev, page: prev.page + 1 }));
        }}
        onEndReachedThreshold={0.1}
      />
    </View>
  );
};

export default NeedsScreen;
```

### ✍️ Criar Nova Necessidade

```javascript
// src/screens/CreateNeedScreen.js
import React, { useState, useEffect } from 'react';
import { 
  View, 
  TextInput, 
  TouchableOpacity, 
  Text, 
  Alert,
  ScrollView 
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { needService } from '../services/needService';
import { categoryService } from '../services/categoryService';
import { authService } from '../services/authService';

const CreateNeedScreen = ({ navigation }) => {
  const [formData, setFormData] = useState({
    titulo: '',
    descricao: '',
    categoria: '',
    subcategoria: '',
    quantidade: '',
    unidade: 'un',
  });
  
  const [categories, setCategories] = useState([]);
  const [subcategories, setSubcategories] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    if (formData.categoria) {
      loadSubcategories(formData.categoria);
    }
  }, [formData.categoria]);

  const loadCategories = async () => {
    try {
      const cats = await categoryService.getCategories();
      setCategories(cats);
    } catch (error) {
      Alert.alert('Erro', 'Falha ao carregar categorias');
    }
  };

  const loadSubcategories = async (categoryId) => {
    try {
      const subcats = await categoryService.getSubcategories(categoryId);
      setSubcategories(subcats);
    } catch (error) {
      console.error('Erro ao carregar subcategorias:', error);
    }
  };

  const handleSubmit = async () => {
    if (!formData.titulo || !formData.categoria || !formData.subcategoria) {
      Alert.alert('Erro', 'Preencha todos os campos obrigatórios');
      return;
    }

    setLoading(true);
    try {
      const currentUser = await authService.getCurrentUser();
      
      const needData = {
        ...formData,
        cliente: currentUser.id,
        quantidade: parseInt(formData.quantidade) || 1,
      };

      const newNeed = await needService.createNeed(needData);
      
      Alert.alert('Sucesso', 'Necessidade criada com sucesso!', [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (error) {
      Alert.alert('Erro', 'Falha ao criar necessidade');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={{ padding: 20 }}>
      <TextInput
        placeholder="Título da necessidade *"
        value={formData.titulo}
        onChangeText={(text) => setFormData(prev => ({ ...prev, titulo: text }))}
        style={{ borderWidth: 1, padding: 10, marginBottom: 15 }}
      />

      <TextInput
        placeholder="Descrição detalhada *"
        value={formData.descricao}
        onChangeText={(text) => setFormData(prev => ({ ...prev, descricao: text }))}
        multiline
        numberOfLines={4}
        style={{ borderWidth: 1, padding: 10, marginBottom: 15, height: 100 }}
      />

      <View style={{ borderWidth: 1, marginBottom: 15 }}>
        <Picker
          selectedValue={formData.categoria}
          onValueChange={(value) => setFormData(prev => ({ 
            ...prev, 
            categoria: value,
            subcategoria: '' // Reset subcategoria
          }))}
        >
          <Picker.Item label="Selecione uma categoria *" value="" />
          {categories.map(cat => (
            <Picker.Item 
              key={cat.id} 
              label={cat.nome} 
              value={cat.id.toString()} 
            />
          ))}
        </Picker>
      </View>

      {formData.categoria && (
        <View style={{ borderWidth: 1, marginBottom: 15 }}>
          <Picker
            selectedValue={formData.subcategoria}
            onValueChange={(value) => setFormData(prev => ({ 
              ...prev, 
              subcategoria: value 
            }))}
          >
            <Picker.Item label="Selecione uma subcategoria *" value="" />
            {subcategories.map(subcat => (
              <Picker.Item 
                key={subcat.id} 
                label={subcat.nome} 
                value={subcat.id.toString()} 
              />
            ))}
          </Picker>
        </View>
      )}

      <View style={{ flexDirection: 'row', marginBottom: 20 }}>
        <TextInput
          placeholder="Quantidade"
          value={formData.quantidade}
          onChangeText={(text) => setFormData(prev => ({ ...prev, quantidade: text }))}
          keyboardType="numeric"
          style={{ 
            borderWidth: 1, 
            padding: 10, 
            flex: 1, 
            marginRight: 10 
          }}
        />
        
        <View style={{ borderWidth: 1, flex: 1 }}>
          <Picker
            selectedValue={formData.unidade}
            onValueChange={(value) => setFormData(prev => ({ ...prev, unidade: value }))}
          >
            <Picker.Item label="Unidade" value="un" />
            <Picker.Item label="Metro" value="m" />
            <Picker.Item label="Metro²" value="m²" />
            <Picker.Item label="Quilo" value="kg" />
            <Picker.Item label="Litro" value="l" />
          </Picker>
        </View>
      </View>

      <TouchableOpacity 
        onPress={handleSubmit}
        disabled={loading}
        style={{ 
          backgroundColor: '#28a745', 
          padding: 15, 
          borderRadius: 5 
        }}
      >
        <Text style={{ color: 'white', textAlign: 'center', fontSize: 16 }}>
          {loading ? 'Criando...' : 'Criar Necessidade'}
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

export default CreateNeedScreen;
```

---

## ⚠️ Tratamento de Erros

### Hook Personalizado para Erro

```javascript
// src/hooks/useErrorHandler.js
import { Alert } from 'react-native';

export const useErrorHandler = () => {
  const handleError = (error, customMessage = null) => {
    console.error('API Error:', error);

    let message = customMessage || 'Ocorreu um erro inesperado';

    if (error.response) {
      // Erro de resposta da API
      const status = error.response.status;
      const data = error.response.data;

      switch (status) {
        case 400:
          message = 'Dados inválidos. Verifique as informações enviadas.';
          break;
        case 401:
          message = 'Sessão expirada. Faça login novamente.';
          break;
        case 403:
          message = 'Você não tem permissão para esta ação.';
          break;
        case 404:
          message = 'Recurso não encontrado.';
          break;
        case 500:
          message = 'Erro interno do servidor. Tente novamente mais tarde.';
          break;
        default:
          message = data.message || data.detail || message;
      }
    } else if (error.request) {
      // Erro de rede
      message = 'Erro de conexão. Verifique sua internet.';
    }

    Alert.alert('Erro', message);
    return message;
  };

  return { handleError };
};
```

### Implementação com Try-Catch

```javascript
// Exemplo de uso
import { useErrorHandler } from '../hooks/useErrorHandler';

const MyComponent = () => {
  const { handleError } = useErrorHandler();

  const fetchData = async () => {
    try {
      const data = await needService.getNeeds();
      // Processar dados...
    } catch (error) {
      handleError(error, 'Falha ao carregar necessidades');
    }
  };

  // ... resto do componente
};
```

---

## ✅ Boas Práticas

### 1. **Gerenciamento de Estado**

```javascript
// src/context/AppContext.js
import React, { createContext, useContext, useReducer } from 'react';

const AppContext = createContext();

const initialState = {
  user: null,
  categories: [],
  loading: false,
  error: null,
};

const appReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_CATEGORIES':
      return { ...state, categories: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    default:
      return state;
  }
};

export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp deve ser usado dentro de AppProvider');
  }
  return context;
};
```

### 2. **Cache de Dados**

```javascript
// src/utils/cache.js
import AsyncStorage from '@react-native-async-storage/async-storage';

export const cache = {
  async set(key, data, ttl = 300000) { // 5 minutos padrão
    const item = {
      data,
      timestamp: Date.now(),
      ttl,
    };
    await AsyncStorage.setItem(`cache_${key}`, JSON.stringify(item));
  },

  async get(key) {
    try {
      const item = await AsyncStorage.getItem(`cache_${key}`);
      if (!item) return null;

      const parsed = JSON.parse(item);
      const now = Date.now();

      if (now - parsed.timestamp > parsed.ttl) {
        await AsyncStorage.removeItem(`cache_${key}`);
        return null;
      }

      return parsed.data;
    } catch {
      return null;
    }
  },

  async clear(key) {
    await AsyncStorage.removeItem(`cache_${key}`);
  },
};

// Uso no serviço
export const categoryService = {
  async getCategories(useCache = true) {
    if (useCache) {
      const cached = await cache.get('categories');
      if (cached) return cached;
    }

    const response = await api.get('categorias/');
    const data = response.data.results;
    
    await cache.set('categories', data);
    return data;
  },
};
```

### 3. **Paginação Infinita**

```javascript
// src/hooks/usePagination.js
import { useState, useEffect } from 'react';

export const usePagination = (fetchFunction, filters = {}) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);

  const loadData = async (isRefresh = false) => {
    if (loading && !isRefresh) return;

    isRefresh ? setRefreshing(true) : setLoading(true);

    try {
      const currentPage = isRefresh ? 1 : page;
      const response = await fetchFunction({ 
        ...filters, 
        page: currentPage 
      });

      if (isRefresh) {
        setData(response.results);
        setPage(2);
      } else {
        setData(prev => [...prev, ...response.results]);
        setPage(prev => prev + 1);
      }

      setHasMore(!!response.next);
    } catch (error) {
      console.error('Pagination error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const refresh = () => loadData(true);
  const loadMore = () => hasMore && loadData();

  return {
    data,
    loading,
    refreshing,
    hasMore,
    refresh,
    loadMore,
  };
};
```

### 4. **Validação de Formulários**

```javascript
// src/utils/validation.js
export const validators = {
  required: (value) => {
    if (!value || value.toString().trim() === '') {
      return 'Este campo é obrigatório';
    }
    return null;
  },

  email: (value) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return 'Email inválido';
    }
    return null;
  },

  minLength: (min) => (value) => {
    if (value.length < min) {
      return `Deve ter pelo menos ${min} caracteres`;
    }
    return null;
  },

  phone: (value) => {
    const phoneRegex = /^\(\d{2}\)\s\d{4,5}-\d{4}$/;
    if (!phoneRegex.test(value)) {
      return 'Telefone inválido. Use: (11) 99999-9999';
    }
    return null;
  },
};

// Hook para validação
export const useFormValidation = (initialValues, validationRules) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});

  const validate = (fieldName, value) => {
    const rules = validationRules[fieldName];
    if (!rules) return null;

    for (const rule of rules) {
      const error = rule(value);
      if (error) return error;
    }
    return null;
  };

  const handleChange = (fieldName, value) => {
    setValues(prev => ({ ...prev, [fieldName]: value }));
    
    const error = validate(fieldName, value);
    setErrors(prev => ({ ...prev, [fieldName]: error }));
  };

  const validateAll = () => {
    const newErrors = {};
    let isValid = true;

    Object.keys(validationRules).forEach(fieldName => {
      const error = validate(fieldName, values[fieldName]);
      newErrors[fieldName] = error;
      if (error) isValid = false;
    });

    setErrors(newErrors);
    return isValid;
  };

  return {
    values,
    errors,
    handleChange,
    validateAll,
  };
};
```

---

## 🔧 Exemplos Completos

### App Principal com Context

```javascript
// App.js
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { AppProvider } from './src/context/AppContext';

import LoginScreen from './src/screens/LoginScreen';
import HomeScreen from './src/screens/HomeScreen';
import NeedsScreen from './src/screens/NeedsScreen';
import CreateNeedScreen from './src/screens/CreateNeedScreen';

const Stack = createStackNavigator();

const App = () => {
  return (
    <AppProvider>
      <NavigationContainer>
        <Stack.Navigator initialRouteName="Login">
          <Stack.Screen 
            name="Login" 
            component={LoginScreen}
            options={{ headerShown: false }}
          />
          <Stack.Screen 
            name="Home" 
            component={HomeScreen}
            options={{ title: 'Necessito' }}
          />
          <Stack.Screen 
            name="Needs" 
            component={NeedsScreen}
            options={{ title: 'Necessidades' }}
          />
          <Stack.Screen 
            name="CreateNeed" 
            component={CreateNeedScreen}
            options={{ title: 'Nova Necessidade' }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </AppProvider>
  );
};

export default App;
```

### Componente de Lista Reutilizável

```javascript
// src/components/NeedsList.js
import React from 'react';
import { 
  FlatList, 
  View, 
  Text, 
  TouchableOpacity, 
  Image,
  RefreshControl 
} from 'react-native';
import { usePagination } from '../hooks/usePagination';
import { needService } from '../services/needService';

const NeedCard = ({ item, onPress }) => (
  <TouchableOpacity 
    style={{
      backgroundColor: 'white',
      margin: 10,
      padding: 15,
      borderRadius: 8,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 3,
    }}
    onPress={() => onPress(item)}
  >
    {item.imagens?.[0] && (
      <Image 
        source={{ uri: item.imagens[0].imagem }}
        style={{ width: '100%', height: 150, borderRadius: 5 }}
        resizeMode="cover"
      />
    )}
    
    <Text style={{ 
      fontSize: 16, 
      fontWeight: 'bold', 
      marginTop: 10 
    }}>
      {item.titulo}
    </Text>
    
    <Text style={{ 
      color: '#666', 
      marginTop: 5,
      lineHeight: 20 
    }}>
      {item.descricao.length > 100 
        ? `${item.descricao.substring(0, 100)}...` 
        : item.descricao
      }
    </Text>
    
    <View style={{ 
      flexDirection: 'row', 
      justifyContent: 'space-between',
      marginTop: 10,
      alignItems: 'center'
    }}>
      <Text style={{ color: '#007bff' }}>
        {item.categoria_nome}
      </Text>
      <Text style={{ color: '#28a745', fontWeight: 'bold' }}>
        {item.status}
      </Text>
    </View>
    
    <Text style={{ 
      color: '#999', 
      fontSize: 12, 
      marginTop: 5 
    }}>
      Por: {item.cliente_nome}
    </Text>
  </TouchableOpacity>
);

const NeedsList = ({ filters = {}, onItemPress }) => {
  const {
    data,
    loading,
    refreshing,
    hasMore,
    refresh,
    loadMore
  } = usePagination(needService.getNeeds, filters);

  const renderFooter = () => {
    if (!loading) return null;
    return (
      <View style={{ padding: 20 }}>
        <Text style={{ textAlign: 'center' }}>Carregando...</Text>
      </View>
    );
  };

  return (
    <FlatList
      data={data}
      renderItem={({ item }) => (
        <NeedCard item={item} onPress={onItemPress} />
      )}
      keyExtractor={item => item.id.toString()}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={refresh}
        />
      }
      onEndReached={loadMore}
      onEndReachedThreshold={0.1}
      ListFooterComponent={renderFooter}
      showsVerticalScrollIndicator={false}
    />
  );
};

export default NeedsList;
```

---

## 📞 Suporte e Recursos Adicionais

### URLs Importantes
- **API Base**: `https://necessito.online/api/`
- **Documentação Swagger**: `https://necessito.online/api/swagger/`
- **Documentação ReDoc**: `https://necessito.online/api/redoc/`

### Códigos de Status HTTP
- **200**: Sucesso
- **201**: Criado com sucesso
- **400**: Dados inválidos
- **401**: Não autenticado
- **403**: Sem permissão
- **404**: Não encontrado
- **500**: Erro interno do servidor

### Contato para Suporte
- **Email**: dev@necessito.online
- **Documentação**: Sempre consulte a documentação Swagger para detalhes atualizados

---

**Desenvolvido pela equipe Necessito** 🚀
*Versão 1.0 - Atualizada em 2025*