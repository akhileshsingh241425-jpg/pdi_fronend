"""
IPQC API Routes
"""
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

from app.services.form_generator import IPQCFormGenerator
from app.services.pdf_generator import IPQCPDFGenerator, SerialNumberGenerator
from app.models.ipqc_data import BOMData

ipqc_bp = Blueprint('ipqc', __name__)

# Initialize services
form_generator = IPQCFormGenerator()


@ipqc_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "IPQC Automation API is running",
        "timestamp": datetime.now().isoformat()
    })


@ipqc_bp.route('/generate-ipqc', methods=['POST'])
def generate_ipqc():
    """
    Generate IPQC form based on inputs
    
    Expected JSON:
    {
        "date": "2024-01-15",
        "shift": "A",
        "customer_id": "GSPL/IPQC/IPC/003",
        "po_number": "PO12345",
        "serial_start": 10001,
        "module_count": 1
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['date', 'shift', 'customer_id', 'po_number']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Extract parameters
        date = data.get('date')
        shift = data.get('shift')
        customer_id = data.get('customer_id')
        po_number = data.get('po_number')
        serial_start = data.get('serial_start', 10001)
        module_count = data.get('module_count', 1)
        
        # Generate IPQC form
        ipqc_form = form_generator.generate_form(
            date=date,
            shift=shift,
            customer_id=customer_id,
            po_number=po_number,
            serial_start=serial_start,
            module_count=module_count
        )
        
        return jsonify({
            "success": True,
            "message": "IPQC form generated successfully",
            "data": ipqc_form
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to generate IPQC form"
        }), 500


@ipqc_bp.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """
    Generate PDF from IPQC form data
    
    Expected JSON:
    {
        "ipqc_data": {...},  // Complete IPQC form data
        "filename": "optional_custom_name.pdf"
    }
    """
    try:
        data = request.get_json()
        
        if 'ipqc_data' not in data:
            return jsonify({
                "error": "Missing ipqc_data in request"
            }), 400
        
        ipqc_data = data['ipqc_data']
        
        # Initialize PDF generator
        pdf_folder = current_app.config['PDF_FOLDER']
        pdf_generator = IPQCPDFGenerator(pdf_folder)
        
        # Generate PDF
        pdf_path = pdf_generator.generate_ipqc_pdf(
            ipqc_data=ipqc_data.get('stages', []),
            bom_data=ipqc_data.get('bom', {}),
            metadata=ipqc_data.get('metadata', {})
        )
        
        # Return PDF file
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=os.path.basename(pdf_path)
        )
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to generate PDF"
        }), 500


@ipqc_bp.route('/generate-complete', methods=['POST'])
def generate_complete():
    """
    Complete workflow: Generate IPQC form and return PDF directly
    
    Expected JSON:
    {
        "date": "2024-01-15",
        "shift": "A",
        "customer_id": "GSPL/IPQC/IPC/003",
        "po_number": "PO12345",
        "serial_start": 10001,
        "module_count": 1
    }
    """
    try:
        data = request.get_json()
        
        # Support both 'customer' and 'customer_id' parameter names
        customer = data.get('customer_id') or data.get('customer') or 'Boeing'
        po_number = data.get('po_number') or f"PO-{data.get('date', '20240115').replace('-', '')}"
        
        # Generate IPQC form
        ipqc_form = form_generator.generate_form(
            date=data.get('date'),
            shift=data.get('shift'),
            customer_id=customer,
            po_number=po_number,
            serial_start=data.get('serial_start', 10001),
            module_count=data.get('module_count', 1)
        )
        
        # Generate PDF
        pdf_folder = current_app.config['PDF_FOLDER']
        pdf_generator = IPQCPDFGenerator(pdf_folder)
        
        pdf_path = pdf_generator.generate_ipqc_pdf(
            ipqc_data=ipqc_form.get('stages', []),
            bom_data=ipqc_form.get('bom', {}),
            metadata=ipqc_form.get('metadata', {})
        )
        
        # Return PDF
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=os.path.basename(pdf_path)
        )
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to generate complete IPQC report"
        }), 500


@ipqc_bp.route('/upload-bom', methods=['POST'])
def upload_bom():
    """
    Upload customer BOM data
    
    Expected JSON:
    {
        "customer_id": "CUST001",
        "bom_data": {
            "customer_name": "...",
            "module_type": "...",
            ...
        }
    }
    """
    try:
        data = request.get_json()
        
        if 'customer_id' not in data or 'bom_data' not in data:
            return jsonify({
                "error": "Missing customer_id or bom_data"
            }), 400
        
        customer_id = data['customer_id']
        bom_data = data['bom_data']
        
        # Store BOM
        success = form_generator.upload_bom(customer_id, bom_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"BOM uploaded successfully for customer: {customer_id}"
            }), 200
        else:
            return jsonify({
                "error": "Failed to upload BOM"
            }), 500
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to upload BOM"
        }), 500


@ipqc_bp.route('/get-bom/<customer_id>', methods=['GET'])
def get_bom(customer_id):
    """Get BOM for specific customer"""
    try:
        bom = BOMData.get_bom(customer_id)
        
        if bom:
            return jsonify({
                "success": True,
                "customer_id": customer_id,
                "bom": bom
            }), 200
        else:
            return jsonify({
                "error": "BOM not found for this customer"
            }), 404
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Failed to retrieve BOM"
        }), 500


@ipqc_bp.route('/list-customers', methods=['GET'])
def list_customers():
    """List all available customers"""
    try:
        customers = list(BOMData.CUSTOMER_BOMS.keys())
        return jsonify({
            "success": True,
            "customers": customers,
            "count": len(customers)
        }), 200
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@ipqc_bp.route('/generate-serials', methods=['POST'])
def generate_serials():
    """
    Generate serial numbers
    
    Expected JSON:
    {
        "start_number": 10001,
        "count": 100,
        "prefix": "GSPL",
        "padding": 5
    }
    """
    try:
        data = request.get_json()
        
        start_number = data.get('start_number', 10001)
        count = data.get('count', 1)
        prefix = data.get('prefix', '')
        padding = data.get('padding', 5)
        
        # Generate serial numbers
        serials = SerialNumberGenerator.generate_serial_numbers(start_number, count)
        
        # Format if prefix provided
        if prefix:
            serials = [
                SerialNumberGenerator.format_serial_number(s, prefix=prefix, padding=padding)
                for s in serials
            ]
        
        return jsonify({
            "success": True,
            "serial_numbers": serials,
            "count": len(serials)
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@ipqc_bp.route('/template-info', methods=['GET'])
def template_info():
    """Get information about IPQC template"""
    try:
        from app.models.ipqc_data import IPQCTemplate
        
        return jsonify({
            "success": True,
            "total_stages": IPQCTemplate.get_stage_count(),
            "total_checkpoints": IPQCTemplate.get_checkpoint_count(),
            "stages": [
                {
                    "sr_no": stage.get("sr_no"),
                    "stage": stage.get("stage"),
                    "checkpoint_count": len(stage.get("checkpoints", []))
                }
                for stage in IPQCTemplate.get_template()
            ]
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
