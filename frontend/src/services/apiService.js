/**
 * API Service for IPQC Backend
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const ipqcService = {
  /**
   * Health check
   */
  healthCheck: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  /**
   * Generate IPQC form
   */
  generateForm: async (formData) => {
    try {
      const response = await apiClient.post('/generate-ipqc', formData);
      return response.data;
    } catch (error) {
      console.error('Form generation failed:', error);
      throw error;
    }
  },

  /**
   * Generate and download PDF
   */
  generatePDF: async (formData) => {
    try {
      const response = await apiClient.post('/generate-complete', formData, {
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `IPQC_Report_${Date.now()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      return { success: true, message: 'PDF downloaded successfully' };
    } catch (error) {
      console.error('PDF generation failed:', error);
      throw error;
    }
  },

  /**
   * Upload BOM
   */
  uploadBOM: async (customerId, bomData) => {
    try {
      const response = await apiClient.post('/upload-bom', {
        customer_id: customerId,
        bom_data: bomData,
      });
      return response.data;
    } catch (error) {
      console.error('BOM upload failed:', error);
      throw error;
    }
  },

  /**
   * Get BOM for customer
   */
  getBOM: async (customerId) => {
    try {
      const response = await apiClient.get(`/get-bom/${customerId}`);
      return response.data;
    } catch (error) {
      console.error('BOM fetch failed:', error);
      throw error;
    }
  },

  /**
   * List all customers
   */
  listCustomers: async () => {
    try {
      const response = await apiClient.get('/list-customers');
      return response.data;
    } catch (error) {
      console.error('Customer list fetch failed:', error);
      throw error;
    }
  },

  /**
   * Generate serial numbers
   */
  generateSerials: async (startNumber, count, prefix = '', padding = 5) => {
    try {
      const response = await apiClient.post('/generate-serials', {
        start_number: startNumber,
        count: count,
        prefix: prefix,
        padding: padding,
      });
      return response.data;
    } catch (error) {
      console.error('Serial generation failed:', error);
      throw error;
    }
  },

  /**
   * Get template information
   */
  getTemplateInfo: async () => {
    try {
      const response = await apiClient.get('/template-info');
      return response.data;
    } catch (error) {
      console.error('Template info fetch failed:', error);
      throw error;
    }
  },
};

export default ipqcService;
