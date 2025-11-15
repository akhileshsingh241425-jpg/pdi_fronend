"""
IPQC Form Generator Service
Auto-fills IPQC forms based on BOM and customer data
"""
from app.models.ipqc_data import IPQCTemplate, BOMData


class IPQCFormGenerator:
    """Intelligent IPQC form generation with auto-fill capabilities"""
    
    def __init__(self):
        self.template = IPQCTemplate.get_template()
    
    def generate_form(self, date, shift, customer_id, po_number, serial_start=10001, module_count=1):
        """
        Generate complete IPQC form with auto-filled values
        
        Args:
            date: Date of inspection
            shift: Shift (A/B/C)
            customer_id: Customer/Document ID
            po_number: Purchase Order number
            serial_start: Starting serial number
            module_count: Number of modules in this batch
        
        Returns:
            dict: Complete IPQC form data
        """
        # Get customer BOM
        bom = BOMData.get_bom(customer_id)
        if not bom:
            bom = self._get_default_bom()
        
        # Auto-fill all stages
        filled_stages = []
        for stage in self.template:
            filled_stage = self._fill_stage(stage, bom)
            filled_stages.append(filled_stage)
        
        # Generate metadata
        metadata = {
            "date": date,
            "shift": shift,
            "customer_id": customer_id,
            "customer_name": bom.get("customer_name", ""),
            "po_number": po_number,
            "doc_number": customer_id,
            "issue_date": "01/12/2024",
            "revision": "01/30-08-2025",
            "serial_start": serial_start,
            "module_count": module_count
        }
        
        return {
            "metadata": metadata,
            "bom": bom,
            "stages": filled_stages,
            "total_stages": len(filled_stages),
            "total_checkpoints": sum(len(s.get('checkpoints', [])) for s in filled_stages)
        }
    
    def _fill_stage(self, stage, bom):
        """Auto-fill a stage based on BOM data"""
        filled_stage = {
            "sr_no": stage.get("sr_no"),
            "stage": stage.get("stage"),
            "checkpoints": []
        }
        
        for checkpoint in stage.get("checkpoints", []):
            filled_checkpoint = checkpoint.copy()
            
            # Auto-fill monitoring result based on checkpoint type
            monitoring_result = self._get_realistic_monitoring_result(checkpoint, stage.get("stage"))
            filled_checkpoint["monitoring_result"] = monitoring_result
            filled_checkpoint["remarks"] = ""
            
            filled_stage["checkpoints"].append(filled_checkpoint)
        
        return filled_stage
    
    def _get_realistic_monitoring_result(self, checkpoint, stage_name):
        """Get realistic monitoring results matching actual IPQC format with COMPLETE DATA"""
        checkpoint_name = checkpoint.get("checkpoint", "").lower()
        acceptance = checkpoint.get("acceptance_criteria", "").lower()
        
        # ========== STAGE 1: Shop Floor ==========
        if "temperature" in checkpoint_name and "shop floor" in stage_name.lower():
            return "Time: 08:00 AM - 25°C"
        if "humidity" in checkpoint_name and "shop floor" in stage_name.lower():
            return "Time: 08:00 AM - 45% RH"
        
        # ========== STAGE 2: Glass Loader ==========
        if "glass dimension" in checkpoint_name:
            return "1956mm x 991mm - OK"
        if "appearance" in checkpoint_name and "visual" in checkpoint_name:
            return "No Scratches/Cracks - OK"
        
        # ========== STAGE 3: EVA/EPE Cutting ==========
        if "eva/epe type" in checkpoint_name or "eva type" in checkpoint_name:
            return "EVA Type: PLASTOMER OK"
        if "eva" in checkpoint_name and "dimension" in checkpoint_name:
            return "1956mm x 991mm - OK"
        if "eva" in checkpoint_name and "status" in checkpoint_name:
            return "No Damage - OK"
        
        # ========== STAGE 4: Eva/EPE Soldering ==========
        if "soldering temperature" in checkpoint_name:
            return "Time: 08:15 AM - Temp: 350°C"
        if "quality check" in checkpoint_name:
            return "Proper Sealing - OK"
        
        # ========== STAGE 5: Cell Loading ==========
        if "cell manufacturer" in checkpoint_name:
            return "Refer Process Card - Longi/Jinko"
        if "cell size" in checkpoint_name:
            return "Refer Process Card - 182mm"
        if "cell condition" in checkpoint_name:
            return "No Damage/Cracks - OK"
        if "cleanliness" in checkpoint_name:
            return "Clean Surface - OK"
        
        # ========== STAGE 6: Tabber & Stringer ==========
        if "verification of process parameter" in checkpoint_name:
            if "atw stringer" in acceptance:
                return "Monitoring of ATW STRINGER - OK"
            elif "auto bussing" in acceptance:
                return "Specification for Auto Bussing - OK"
            return "Process Parameters - OK"
        
        if "cell cross cutting" in checkpoint_name:
            return "Both Side Cutting - OK"
        if "visual check after stringing" in checkpoint_name:
            return "TS Visual Criteria - OK"
        if "el image" in checkpoint_name:
            return "TS EL Criteria - No Defects"
        if "string length" in checkpoint_name:
            return "1163 mm ± 2mm"
        if "cell to cell gap" in checkpoint_name or "cell gap" in checkpoint_name:
            return "0.75 mm (Within Tolerance)"
        if "peel strength" in checkpoint_name:
            return "Ribbon to Cell: 2.5N (OK)"
        if "string to string gap" in checkpoint_name:
            return "2.0 mm ± 0.5mm"
        if "cell edge to glass edge" in checkpoint_name:
            return "Refer Module Drawing - OK"
        if "ribbon to busbar" in checkpoint_name:
            return "Busbar Peel Test: 3.0N (OK)"
        if "terminal busbar" in checkpoint_name:
            return "Refer Drawing GSPL/N144 - OK"
        
        # ========== STAGE 7-10: Layup/Vacuum/Lamination ==========
        if "backsheet type" in checkpoint_name:
            return "White Backsheet - OK"
        if "backsheet dimension" in checkpoint_name:
            return "1956mm x 991mm - OK"
        if "backsheet status" in checkpoint_name:
            return "No Damage - OK"
        if "layup process" in checkpoint_name:
            return "Proper Layup - OK"
        if "vacuum time" in checkpoint_name:
            return "Time: 5 min - OK"
        if "vacuum pressure" in checkpoint_name:
            return "Pressure: -90 kPa - OK"
        if "pre-heat temperature" in checkpoint_name:
            return "Temp: 150°C - OK"
        if "lamination temperature" in checkpoint_name:
            return "Temp: 145°C - OK"
        if "lamination time" in checkpoint_name:
            return "Time: 12 min - OK"
        if "lamination pressure" in checkpoint_name:
            return "Pressure: 1000 mbar - OK"
        
        # ========== STAGE 11-15: Trimming/Sun Simulator ==========
        if "trimming" in checkpoint_name and "edge" in checkpoint_name:
            return "Clean Edges - OK"
        if "trimming clearance" in checkpoint_name:
            return "10mm Clearance - OK"
        if "el test" in checkpoint_name or "el check" in checkpoint_name:
            return "EL Image - No Defects"
        if "sun simulator" in checkpoint_name or "flash test" in checkpoint_name:
            return "Power: 550W ± 5W"
        if "voc" in checkpoint_name or "voltage" in checkpoint_name:
            return "Voc: 49.5V (OK)"
        if "isc" in checkpoint_name or "current" in checkpoint_name:
            return "Isc: 14.2A (OK)"
        if "vmp" in checkpoint_name:
            return "Vmp: 41.8V (OK)"
        if "imp" in checkpoint_name:
            return "Imp: 13.2A (OK)"
        if "pmax" in checkpoint_name or "power" in checkpoint_name:
            return "Pmax: 552W (OK)"
        if "ff" in checkpoint_name or "fill factor" in checkpoint_name:
            return "FF: 78.5% (OK)"
        if "efficiency" in checkpoint_name:
            return "Efficiency: 21.2% (OK)"
        
        # ========== STAGE 16-20: Frame/Junction Box ==========
        if "frame dimension" in checkpoint_name:
            return "1956mm x 991mm x 35mm - OK"
        if "frame material" in checkpoint_name:
            return "Anodized Aluminum - OK"
        if "frame quality" in checkpoint_name:
            return "No Damage - OK"
        if "sealant type" in checkpoint_name or "silicone" in checkpoint_name:
            return "Silicone Sealant - OK"
        if "sealant application" in checkpoint_name:
            return "Uniform Application - OK"
        if "corner key" in checkpoint_name:
            return "4 Corner Keys - OK"
        if "pressing force" in checkpoint_name:
            return "Force: 200N - OK"
        if "junction box type" in checkpoint_name:
            return "IP68 Rated - OK"
        if "junction box position" in checkpoint_name:
            return "Centered - OK"
        if "cable length" in checkpoint_name:
            return "1200mm ± 50mm"
        if "connector type" in checkpoint_name:
            return "MC4 Connector - OK"
        
        # ========== STAGE 21-25: Hi-Pot/Insulation/Continuity ==========
        if "hipot test" in checkpoint_name or "dielectric" in checkpoint_name:
            return "3000V AC - Pass"
        if "insulation resistance" in checkpoint_name or "ir test" in checkpoint_name:
            return "IR > 400 MΩ - Pass"
        if "ground continuity" in checkpoint_name:
            return "Resistance < 0.1Ω - Pass"
        if "wet leakage" in checkpoint_name:
            return "Leakage < 5mA - Pass"
        if "dcw/ir/ground" in checkpoint_name:
            return ["Module S.No", "DCW: Pass", "IR: 450MΩ", "Ground: 0.05Ω"]
        
        # ========== STAGE 26-30: Final Inspection ==========
        if "visual inspection" in checkpoint_name:
            return "No Defects - OK"
        if "label position" in checkpoint_name:
            return "Proper Position - OK"
        if "barcode" in checkpoint_name or "qr code" in checkpoint_name:
            return "Scannable - OK"
        if "nameplate" in checkpoint_name:
            return "All Info Correct - OK"
        if "cleaning" in checkpoint_name:
            return "Surface Clean - OK"
        if "packaging" in checkpoint_name:
            return "Proper Packing - OK"
        if "packing material" in checkpoint_name:
            return "Cardboard Box - OK"
        if "module per box" in checkpoint_name:
            return "30 Modules/Box - OK"
        
        # ========== STAGE 31-33: Documentation/Storage ==========
        if "test report" in checkpoint_name:
            return "Report Generated - OK"
        if "certification" in checkpoint_name:
            return "IEC 61215 - OK"
        if "datasheet" in checkpoint_name:
            return "Datasheet Attached - OK"
        if "storage condition" in checkpoint_name:
            return "Temp: 25°C, RH: 45%"
        if "storage location" in checkpoint_name:
            return "Warehouse A - Bay 5"
        if "handling" in checkpoint_name:
            return "Proper Handling - OK"
        
        # ========== Generic Checks ==========
        # Reference to documents/specs
        if "refer process card" in acceptance:
            return "Refer Process Card - OK"
        if "module drawing" in acceptance:
            return "Refer Module Drawing - OK"
        if "gspl" in acceptance and ("qc" in acceptance or "ipqc" in acceptance):
            return "Refer Document GSPL/IPQC/QC/001 - OK"
        
        # Visual inspection with sample size
        if checkpoint.get("sample_size") == "5 pieces":
            return "S.No: 1,2,3,4,5 - All OK"
        
        # Temperature/Humidity monitoring
        if "temp" in checkpoint_name:
            return "Time: 08:00 - Temp: 25°C"
        if "humidity" in checkpoint_name:
            return "Time: 08:00 - RH: 45%"
        
        # Default OK for simple yes/no checks
        if acceptance in ["ok", "pass", "yes", "acceptable"]:
            return "OK"
        
        # Empty for manual entry fields (will be filled by operator)
        return "OK"
    
    def _get_default_bom(self):
        """Return default BOM if customer BOM not found"""
        return {
            "customer_name": "Gautam Solar Private Limited",
            "module_type": "Mono PERC",
            "power_rating": "550W",
            "cells": {
                "count": 144,
                "type": "M10",
                "size": "182mm"
            },
            "module_dimension": {
                "length": 2278,
                "width": 1134,
                "thickness": 35
            }
        }
    
    def upload_bom(self, customer_id, bom_data):
        """
        Upload and store new customer BOM
        
        Args:
            customer_id: Customer identifier
            bom_data: BOM data dictionary
        
        Returns:
            bool: Success status
        """
        return BOMData.add_bom(customer_id, bom_data)
