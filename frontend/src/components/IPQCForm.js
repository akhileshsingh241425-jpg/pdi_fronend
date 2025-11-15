/**
 * Main IPQC Form Component
 */
import React, { useState, useEffect } from 'react';
import ipqcService from '../services/apiService';
import '../styles/IPQCForm.css';

const IPQCForm = () => {
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    shift: 'A',
    customer_id: 'GSPL/IPQC/IPC/003',
    po_number: '',
    serial_start: 10001,
    module_count: 1,
  });

  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [templateInfo, setTemplateInfo] = useState(null);

  useEffect(() => {
    loadCustomers();
    loadTemplateInfo();
  }, []);

  const loadCustomers = async () => {
    try {
      const response = await ipqcService.listCustomers();
      if (response.success) {
        setCustomers(response.customers);
      }
    } catch (error) {
      console.error('Failed to load customers:', error);
    }
  };

  const loadTemplateInfo = async () => {
    try {
      const response = await ipqcService.getTemplateInfo();
      if (response.success) {
        setTemplateInfo(response);
      }
    } catch (error) {
      console.error('Failed to load template info:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleGenerateForm = async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await ipqcService.generateForm(formData);
      if (response.success) {
        setMessage({
          type: 'success',
          text: `✅ IPQC form generated successfully! ${response.data.total_stages} stages, ${response.data.total_checkpoints} checkpoints.`,
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: `❌ Failed to generate form: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePDF = async () => {
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      await ipqcService.generatePDF(formData);
      setMessage({
        type: 'success',
        text: '✅ PDF generated and downloaded successfully!',
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: `❌ Failed to generate PDF: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ipqc-container">
      <div className="header">
        <div className="logo">
          <h1>GAUTAM</h1>
          <p>SOLAR</p>
        </div>
        <div className="title">
          <h2>IPQC Automation System</h2>
          <p>Automatic In-Process Quality Check Report Generator</p>
        </div>
      </div>

      {templateInfo && (
        <div className="info-banner">
          <p>
            📋 <strong>{templateInfo.total_stages} Stages</strong> | 
            ✓ <strong>{templateInfo.total_checkpoints} Checkpoints</strong> | 
            🤖 <strong>Fully Automated</strong>
          </p>
        </div>
      )}

      <div className="form-card">
        <h3>Generate IPQC Report</h3>
        
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="date">
              📅 Date <span className="required">*</span>
            </label>
            <input
              type="date"
              id="date"
              name="date"
              value={formData.date}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="shift">
              🕐 Shift <span className="required">*</span>
            </label>
            <select
              id="shift"
              name="shift"
              value={formData.shift}
              onChange={handleInputChange}
              required
            >
              <option value="A">Shift A</option>
              <option value="B">Shift B</option>
              <option value="C">Shift C</option>
            </select>
          </div>

          <div className="form-group full-width">
            <label htmlFor="customer_id">
              🏢 Customer / Document ID <span className="required">*</span>
            </label>
            <select
              id="customer_id"
              name="customer_id"
              value={formData.customer_id}
              onChange={handleInputChange}
              required
            >
              {customers.map((customer) => (
                <option key={customer} value={customer}>
                  {customer}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group full-width">
            <label htmlFor="po_number">
              📄 PO Number <span className="required">*</span>
            </label>
            <input
              type="text"
              id="po_number"
              name="po_number"
              value={formData.po_number}
              onChange={handleInputChange}
              placeholder="Enter Purchase Order Number"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="serial_start">
              🔢 Starting Serial Number
            </label>
            <input
              type="number"
              id="serial_start"
              name="serial_start"
              value={formData.serial_start}
              onChange={handleInputChange}
              min="1"
            />
          </div>

          <div className="form-group">
            <label htmlFor="module_count">
              📦 Module Count
            </label>
            <input
              type="number"
              id="module_count"
              name="module_count"
              value={formData.module_count}
              onChange={handleInputChange}
              min="1"
            />
          </div>
        </div>

        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <div className="button-group">
          <button
            className="btn btn-secondary"
            onClick={handleGenerateForm}
            disabled={loading || !formData.po_number}
          >
            {loading ? '⏳ Generating...' : '📋 Preview Form'}
          </button>
          
          <button
            className="btn btn-primary"
            onClick={handleGeneratePDF}
            disabled={loading || !formData.po_number}
          >
            {loading ? '⏳ Generating...' : '📥 Generate & Download PDF'}
          </button>
        </div>
      </div>

      <div className="features">
        <h3>✨ Key Features</h3>
        <div className="features-grid">
          <div className="feature-card">
            <h4>🤖 Auto-Fill</h4>
            <p>Automatically fills all 33 stages and 200+ checkpoints based on BOM</p>
          </div>
          <div className="feature-card">
            <h4>📏 Smart Tolerances</h4>
            <p>Applies correct tolerances for each checkpoint automatically</p>
          </div>
          <div className="feature-card">
            <h4>🔢 Serial Numbers</h4>
            <p>Auto-generates and increments serial numbers</p>
          </div>
          <div className="feature-card">
            <h4>📄 Professional PDF</h4>
            <p>Generates production-ready PDF reports instantly</p>
          </div>
        </div>
      </div>

      <footer className="footer">
        <p>© 2024 Gautam Solar Private Limited | IPQC Automation System v1.0</p>
      </footer>
    </div>
  );
};

export default IPQCForm;
