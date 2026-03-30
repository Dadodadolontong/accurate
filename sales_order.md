GET https://zeus.accurate.id/accurate/api/sales-order/detail.do
Params: {
  "number": "SO.0326-651"
}
------------------------------------------------------------
HTTP 200
------------------------------------------------------------
Top-level keys: ['s', 'd']
  s (success) : True
  sp          : None
  d           : dict  keys=['printUserName', 'charField8', 'charField9', 'tax4Amount', 'charField6', 'tax1Rate', 'charField7', 'numericField10', 'charField4', 'foodDelivery', 'charField5', 'optLock', 'percentTaxable', 'receiveItem', 'number', 'printedTime', 'processHistory', 'downPaymentHistory', 'charField2', 'charField3', 'charField1', 'id', 'currencyId', 'transDateView', 'hasStatusHistory', 'dateField2', 'branchId', 'tax1Id', 'dateField1', 'materialAllocation', 'taxable', 'salesInvoice', 'billOfMaterial', 'employeeLoanSettlement', 'purchaseInvoice', 'shipDate', 'tax1Amount', 'salesOrder', 'commentCount', 'transferOrder', 'detailExpense', 'hasNPWP', 'detailItem', 'employeePayment', 'taxableAmount2', 'expenseAccrual', 'taxableAmount1', 'salesReturn', 'lastCashDiscPercent', 'taxableAmount4', 'poNumber', 'charField10', 'status', 'processStages', 'employeeLoanInstallment', 'bankTransfer', 'preliminarySurvey', 'employeeLoan', 'availableDownPayment', 'jobOrder', 'customerClaim', 'journal', 'salesAmount', 'deliveryPacking', 'customerId', 'percentTaxablePrecision', 'statusName', 'currency', 'vendorPrice', 'paymentTermId', 'tax4Rate', 'tax4Id', 'fobId', 'autoCloseChecked', 'deliveryOrder', 'salesDownPayment', 'onlineOrderId', 'approvalTypeNumberId', 'purchaseReturn', 'onlineOrder', 'totalDownPaymentUsed', 'canProcessToPurchaseOrder', 'totalExpense', 'percentShipped', 'inclusiveTax', 'stockOpnameResult', 'taxableDiscount4', 'exchangeInvoice', 'taxableDiscount2', 'subTotal', 'lastCashDiscount', 'taxableDiscount1', 'toAddress', 'rollOver', 'paymentPointOnlineBank', 'employeeLoanDisbursement', 'manufactureOrder', 'totalReturnDownPayment', 'tax2Rate', 'itemAdjustment', 'finishedProject', 'closeReason', 'forceCalculatePercentTaxable', 'periodEnd', 'workOrder', 'masterSalesmanId', 'purchaseDownPayment', 'shipment', 'canProcess', 'assetTransfer', 'recurringDetailId', 'stockOpnameOrder', 'dpUsedHistory', 'salesCheckIn', 'totalAmount', 'downPayments', 'shipDateView', 'salesQuotation', 'fixedAssetEdited', 'manualApprovalNumber', 'fob', 'purchaseRequisition', 'paymentTerm', 'dppAmount', 'finishedGoodSlip', 'tax2Amount', 'purchasePayment', 'description', 'otherDeposit', 'otherPayment', 'tax1', 'availableInputDownPayment', 'costDistribution', 'tax2', 'manualClosedVisible', 'budgetPlan', 'itemTransfer', 'vendorClaim', 'rate', 'forceCalculateTaxRate', 'transDate', 'manualClosed', 'cashDiscount', 'salesReceipt', 'tax3Amount', 'materialEquipment', 'tax4', 'approvalStatus', 'cashDiscPercent', 'tax2Id', 'attachmentExist', 'materialSlip', 'autoCloseVisible', 'sellingPriceAdjustment', 'materialAdjustment', 'totalDownPayment', 'autoCloseRange', 'numericField9', 'checkInId', 'numericField8', 'numericField7', 'createdBy', 'shipmentId', 'numericField6', 'numericField5', 'numericField4', 'purchaseOrder', 'numericField3', 'fixedAsset', 'numericField2', 'attachmentCount', 'numericField1', 'standardProductCost', 'userPrinted', 'customer']

============================================================
FULL RAW JSON
============================================================
{
  "s": true,
  "d": {
    "printUserName": "Belum cetak/email",
    "charField8": "",
    "charField9": "",
    "tax4Amount": 0.0,
    "charField6": "",
    "tax1Rate": 11.0,
    "charField7": "",
    "numericField10": 0.0,
    "charField4": "",
    "foodDelivery": false,
    "charField5": "",
    "optLock": 8,
    "percentTaxable": 100.0,
    "receiveItem": false,
    "number": "SO.0326-651",
    "printedTime": null,
    "processHistory": [
      {
        "approvalStatus": "APPROVED",
        "historyDate": "17/03/2026",
        "historyNumber": "DO.0326.666",
        "historyType": "DO",
        "index": 0,
        "id": 77087
      },
      {
        "approvalStatus": "APPROVED",
        "historyDate": "17/03/2026",
        "historyNumber": "SI.0326.695",
        "historyAmount": 644475.0,
        "historyType": "SI",
        "index": 1,
        "historyOwing": 644475.0,
        "id": 117208
      }
    ],
    "downPaymentHistory": [],
    "charField2": "",
    "charField3": "",
    "charField1": "",
    "id": 82994,
    "currencyId": 50,
    "transDateView": "17 Mar 2026",
    "hasStatusHistory": true,
    "dateField2": null,
    "branchId": 50,
    "tax1Id": 50,
    "dateField1": null,
    "materialAllocation": false,
    "taxable": true,
    "salesInvoice": false,
    "billOfMaterial": false,
    "employeeLoanSettlement": false,
    "purchaseInvoice": false,
    "shipDate": "17/03/2026",
    "tax1Amount": 53276.0,
    "salesOrder": true,
    "commentCount": 0,
    "transferOrder": false,
    "detailExpense": [
      {
        "salesOrderId": 82994,
        "dataClassification10": null,
        "detailName": "B. Transport Barang - Bintaro",
        "departmentId": null,
        "optLock": 0,
        "project": null,
        "expenseName": "B. Transport Barang - Bintaro",
        "expenseAmount": 106875.0,
        "dataClassification10Id": null,
        "dataClassification9Id": null,
        "id": 63410,
        "dataClassification8Id": null,
        "department": null,
        "dataClassification7Id": null,
        "salesQuotationId": null,
        "dataClassification6Id": null,
        "seq": 1,
        "dataClassification5Id": null,
        "dataClassification4Id": null,
        "dataClassification1": null,
        "dataClassification3Id": null,
        "dataClassification2Id": null,
        "amount": 106875.0,
        "dataClassification3": null,
        "dataClassification1Id": null,
        "dataClassification2": null,
        "dataClassification5": null,
        "dataClassification4": null,
        "dataClassification7": null,
        "dataClassification6": null,
        "dataClassification9": null,
        "dataClassification8": null,
        "salesOrder": {
          "number": "SO.0326-651",
          "id": 82994
        },
        "accountId": 461,
        "expenseNotes": null,
        "projectId": null,
        "account": {
          "no": "56102.02",
          "sub": true,
          "parent": {
            "no": "56102",
            "sub": true,
            "parent": {
              "no": "56000",
              "sub": false,
              "parent": {
                "no": null,
                "sub": false,
                "parent": null,
                "lvl": 0,
                "accountType": null,
                "optLock": 0,
                "memo": null,
                "accountTypeName": "",
                "nameWithIndent": "Root",
                "parentNode": true,
                "suspended": false,
                "autoNumberTransactionId": null,
                "nameWithIndentStrip": "Root",
                "fiscal": false,
                "noWithIndent": "null",
                "name": "Root",
                "id": 50,
                "currencyId": null
              },
              "lvl": 1,
              "accountType": "EXPENSE",
              "optLock": 0,
              "memo": null,
              "accountTypeName": "Beban",
              "nameWithIndent": "Biaya Logistik - BAN",
              "parentNode": true,
              "suspended": false,
              "autoNumberTransactionId": null,
              "nameWithIndentStrip": "Biaya Logistik - BAN",
              "fiscal": false,
              "noWithIndent": "56000",
              "name": "Biaya Logistik - BAN",
              "id": 452,
              "currencyId": 50
            },
            "lvl": 2,
            "accountType": "EXPENSE",
            "optLock": 0,
            "memo": null,
            "accountTypeName": "Beban",
            "nameWithIndent": "&nbsp;&nbsp;&nbsp;&nbsp;Transportasi barang - BAN",
            "parentNode": true,
            "suspended": false,
            "autoNumberTransactionId": null,
            "nameWithIndentStrip": "- Transportasi barang - BAN",
            "fiscal": false,
            "noWithIndent": "&nbsp;&nbsp;&nbsp;&nbsp;56102",
            "name": "Transportasi barang - BAN",
            "id": 459,
            "currencyId": 50
          },
          "lvl": 3,
          "accountType": "EXPENSE",
          "optLock": 1,
          "memo": null,
          "accountTypeName": "Beban",
          "nameWithIndent": "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;B. Transport Barang - Bintaro",
          "parentNode": false,
          "suspended": false,
          "autoNumberTransactionId": null,
          "nameWithIndentStrip": "- - B. Transport Barang - Bintaro",
          "fiscal": false,
          "noWithIndent": "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;56102.02",
          "name": "B. Transport Barang - Bintaro",
          "id": 461,
          "currencyId": 50
        }
      }
    ],
    "hasNPWP": true,
    "detailItem": [
      {
        "lastItemDiscPercent": "",
        "charField8": null,
        "charField9": null,
        "processQuantityDesc": "4 VP",
        "charField6": null,
        "charField7": null,
        "numericField10": 0.0,
        "charField4": null,
        "departmentId": null,
        "charField5": null,
        "optLock": 21,
        "itemUnit": {
          "codeUnitTax": null,
          "optLock": 0,
          "name": "VP",
          "id": 1000
        },
        "salesOrderPoNumber": null,
        "availableUnitRatio": 1.0,
        "defaultWarehouseDeliveryOrder": {
          "scrapWarehouse": false,
          "defaultWarehouse": false,
          "locationId": 805,
          "optLock": 5,
          "name": "Gudang Bogor (FG)",
          "description": "Pencatatan lokasi Barang Jadi di Bogor",
          "pic": null,
          "id": 300,
          "suspended": false
        },
        "charField2": null,
        "charField3": null,
        "charField1": null,
        "id": 92569,
        "salesman3Id": null,
        "discountRule": [
          {
            "minQuantity": 0,
            "spaId": null,
            "transDate": "2026-03-28",
            "discountFromSpa": false,
            "unitId": 1000,
            "discount": ""
          },
          {
            "minQuantity": 0,
            "spaId": null,
            "transDate": "2026-03-28",
            "discountFromSpa": false,
            "unitId": 3000,
            "discount": ""
          }
        ],
        "dataClassification6Id": null,
        "salesQuotationDetailId": null,
        "unitPrice": 134400.0,
        "useTax1": true,
        "dateField2": null,
        "dataClassification1": null,
        "salesmanName": "Siti Nurani",
        "branchId": 50,
        "useTax3": false,
        "item": {
          "unit2Id": 3000,
          "charField8": null,
          "charField9": null,
          "charField6": null,
          "charField7": null,
          "numericField10": null,
          "unit4Price": 0.0,
          "charField4": null,
          "charField5": null,
          "optLock": 49,
          "percentTaxable": 100.0,
          "itemBrandId": null,
          "ratioVendorUnit": 1.0,
          "unit3Price": 0.0,
          "salesDiscountGlAccountId": 1007,
          "itemProduced": false,
          "charField2": null,
          "charField3": null,
          "charField1": null,
          "id": 613,
          "maxOptionModifier": null,
          "unitPrice": 134400.0,
          "dateField2": null,
          "branchId": null,
          "tax1Id": 50,
          "dateField1": null,
          "onSales": 0.0,
          "useWholesalePrice": false,
          "unit5Price": 0.0,
          "unit2Price": 672000.0,
          "suspended": false,
          "goodTransitGlAccountId": 117,
          "cogsGlAccountId": 178,
          "referenceSubstitutionId": null,
          "itemSubstitutionId": null,
          "shortName": "Alanabi Value Pack",
          "charField10": null,
          "unBilledGlAccountId": 151,
          "canChangeDetailGroup": false,
          "variantLabel2": null,
          "dimWidth": 0.0,
          "variantLabel1": null,
          "unit3Id": null,
          "salesRetGlAccountId": 1004,
          "dimDepth": 0.0,
          "minimumQuantityReorder": 0.0,
          "lockTime": null,
          "vendorPrice": 0.0,
          "minimumQuantity": 0.0,
          "tax4Id": null,
          "dimHeight": 0.0,
          "additionalCost": false,
          "unit4Id": null,
          "notes": null,
          "purchaseRetGlAccountId": 800,
          "unit1": {
            "codeUnitTax": null,
            "optLock": 0,
            "name": "VP",
            "id": 1000
          },
          "variantParentId": null,
          "unit2": {
            "codeUnitTax": null,
            "optLock": 0,
            "name": "KARTON",
            "id": 3000
          },
          "unit3": null,
          "vendorUnit": {
            "codeUnitTax": null,
            "optLock": 0,
            "name": "VP",
            "id": 1000
          },
          "preferedVendorId": null,
          "ratio2": 5.0,
          "unit4": null,
          "unit5": null,
          "ratio4": 0.0,
          "ratio3": 0.0,
          "ratio5": 0.0,
          "variantDetail2": null,
          "tax3Id": null,
          "variantDetail1": null,
          "inventoryGlAccountId": 800,
          "weight": null,
          "controlQuantity": false,
          "upcNo": null,
          "substituted": false,
          "minOptionModifier": 1.0,
          "salesGlAccountId": 164,
          "name": "Alanabi Value Pack 40 PCS",
          "deliveryLeadTime": 0.0,
          "manageExpired": true,
          "no": "FG-VP40PCS-00",
          "defaultDiscount": null,
          "itemType": "INVENTORY",
          "unit1Id": 1000,
          "unit5Id": null,
          "itemCategoryId": 151,
          "hasImage": false,
          "tax1": {
            "pphPs4Type": null,
            "purchaseTaxGlAccountId": 75,
            "pph23Type": null,
            "optLock": 1,
            "description": "Pajak Pertambahan Nilai",
            "pph15Type": null,
            "taxCode": "PPN",
            "taxInfo": "PPN 11%",
            "pph22Type": null,
            "rate": 11.0,
            "salesTaxGlAccountId": 74,
            "id": 50,
            "taxType": "PPN"
          },
          "tax2": null,
          "manageSN": false,
          "materialProduced": false,
          "variantSeq": null,
          "codeItemTax": null,
          "tax3": null,
          "tax4": null,
          "serialNumberType": "BATCH",
          "tax2Id": null,
          "cost": 0.0,
          "printDetailGroup": false,
          "calculateGroupPrice": false,
          "numericField9": null,
          "defStandardCost": 0.0,
          "numericField8": null,
          "minimumSellingQuantity": 0.0,
          "numericField7": null,
          "numericField6": null,
          "numericField5": null,
          "numericField4": null,
          "numericField3": null,
          "numericField2": null,
          "numericField1": null,
          "vendorUnitId": 1000,
          "unit1Price": 134400.0
        },
        "dataClassification3": null,
        "dataClassification1Id": null,
        "useTax2": false,
        "dateField1": null,
        "dataClassification2": null,
        "dataClassification5": null,
        "dataClassification4": null,
        "availableItemUnitName": "VP",
        "dataClassification7": null,
        "dataClassification6": null,
        "dataClassification9": null,
        "dataClassification8": null,
        "tax1Amount": 53275.675676,
        "detailNotes": null,
        "warehouse": {
          "scrapWarehouse": false,
          "defaultWarehouse": false,
          "locationId": 805,
          "optLock": 5,
          "name": "Gudang Bogor (FG)",
          "description": "Pencatatan lokasi Barang Jadi di Bogor",
          "pic": null,
          "id": 300,
          "suspended": false
        },
        "salesOrder": {
          "number": "SO.0326-651",
          "taxable": true,
          "inclusiveTax": true,
          "id": 82994
        },
        "itemId": 613,
        "warehouseId": 300,
        "charField15": null,
        "charField13": null,
        "charField14": null,
        "charField11": null,
        "charField12": null,
        "useTax4": false,
        "charField10": null,
        "canChangeDetailGroup": false,
        "dataClassification10": null,
        "detailName": "Alanabi Value Pack 40 PCS",
        "lastItemCashDiscount": 0.0,
        "totalPrice": 537600.0,
        "groupSeq": null,
        "transferQuantity": 0.0,
        "salesAmount": 484324.324324,
        "dataClassification7Id": null,
        "seq": 1,
        "availableQuantity": 0.0,
        "dataClassification2Id": null,
        "salesman2Id": null,
        "onlineOrderDetailId": null,
        "onlineOrderId": null,
        "closed": true,
        "onlineOrder": null,
        "salesOrderId": 82994,
        "onlineOrderDetail": null,
        "project": null,
        "quantityDefault": 4.0,
        "itemDiscPercent": "",
        "dataClassification8Id": null,
        "salesQuotationId": null,
        "salesman5Id": null,
        "availableItemCashDiscount": 0.0,
        "dataClassification3Id": null,
        "salesman1Id": 350,
        "tax3Id": null,
        "availableUnitPrice": 134400.0,
        "grossAmount": 484324.324324,
        "poQuantity": 0.0,
        "projectId": null,
        "dppAmount": 484324.324324,
        "tax2Amount": 0.0,
        "unitPriceRule": [
          {
            "minQuantity": 0.0,
            "price": 134400.0,
            "spaId": 2951,
            "unitId": 1000,
            "priceFromSpa": true,
            "minimumPrice": 0.0
          },
          {
            "minQuantity": 0,
            "price": 672000.0,
            "unitId": 3000,
            "priceFromSpa": false,
            "minimumPrice": 0
          }
        ],
        "availableTotalPrice": 537600.0,
        "manualClosedVisible": false,
        "dataClassification10Id": null,
        "itemCashDiscount": 0.0,
        "dataClassification9Id": null,
        "salesmanList": [
          {
            "resignMonth": null,
            "departmentId": null,
            "optLock": 5,
            "joinDateView": "28 Apr 2022",
            "resignYear": null,
            "contactInfoId": 2609,
            "bankName": "BANK CIMB NIAGA",
            "startMonthPayment": 5,
            "nikNo": "3202075608970003",
            "addressId": 3010,
            "number": "BAN016",
            "joinDate": "28/04/2022",
            "salesmanUserId": null,
            "nettoIncomeBefore": 0.0,
            "id": 350,
            "pphBefore": 0.0,
            "posRoleId": 51,
            "startYearPayment": 2022,
            "employeeTaxStatus": "TK0",
            "bankAccount": "762755768800",
            "bankAccountName": "Siti Nurani",
            "domisiliType": "INA",
            "branchId": 50,
            "bankCode": "022",
            "attachmentExist": false,
            "calculatePtkp": true,
            "pph": false,
            "npwpNo": null,
            "suspended": false,
            "employeeWorkStatus": "PEGAWAI_TETAP",
            "name": "Siti Nurani",
            "salesman": true,
            "resign": false
          }
        ],
        "manualClosed": false,
        "department": null,
        "salesman4Id": null,
        "tax3": null,
        "detailTaxName": "PPN 11%",
        "dataClassification5Id": null,
        "dataClassification4Id": null,
        "quantity": 4.0,
        "defaultWarehouseSalesInvoice": {
          "scrapWarehouse": false,
          "defaultWarehouse": false,
          "locationId": 805,
          "optLock": 5,
          "name": "Gudang Bogor (FG)",
          "description": "Pencatatan lokasi Barang Jadi di Bogor",
          "pic": null,
          "id": 300,
          "suspended": false
        },
        "manufactureOrderDetailId": null,
        "shipQuantity": 4.0,
        "numericField9": 0.0,
        "numericField8": 0.0,
        "numericField7": 0.0,
        "numericField6": 0.0,
        "numericField5": 0.0,
        "numericField4": 0.0,
        "itemUnitId": 1000,
        "numericField3": 0.0,
        "numericField2": 0.0,
        "numericField1": 0.0,
        "availableItemUnit": {
          "codeUnitTax": null,
          "optLock": 0,
          "name": "VP",
          "id": 1000
        },
        "unitRatio": 1.0
      }
    ],
    "employeePayment": false,
    "taxableAmount2": 0.0,
    "expenseAccrual": false,
    "taxableAmount1": 484324.324324,
    "salesReturn": false,
    "lastCashDiscPercent": "",
    "taxableAmount4": 0.0,
    "poNumber": null,
    "charField10": "",
    "status": "PROCEED",
    "processStages": false,
    "employeeLoanInstallment": false,
    "bankTransfer": false,
    "preliminarySurvey": false,
    "employeeLoan": false,
    "availableDownPayment": 0.0,
    "jobOrder": false,
    "customerClaim": false,
    "journal": false,
    "salesAmount": 484324.324324,
    "deliveryPacking": false,
    "customerId": 78213,
    "percentTaxablePrecision": 100.0,
    "statusName": "Terproses",
    "currency": {
      "defaultArAccountId": 108,
      "symbol": "Rp",
      "code": "IDR",
      "defaultSalesDiscAccountId": 1007,
      "optLock": 10,
      "currencyConverterType": "TO_LOCAL",
      "defaultAdvSalesAccountId": 59,
      "exchangeRateSymbolCode": "Rp",
      "defaultAdvPurchaseAccountId": 58,
      "defaultRealizeGlAccountId": 550,
      "name": "Indonesian Rupiah",
      "codeSymbol": "IDR Rp",
      "id": 50,
      "defaultApAccountId": 56,
      "defaultUnrealizeGlAccountId": 551,
      "converterTypeName": "1 IDR=XXX IDR"
    },
    "vendorPrice": false,
    "paymentTermId": 1800,
    "tax4Rate": 0.0,
    "tax4Id": null,
    "fobId": null,
    "autoCloseChecked": false,
    "deliveryOrder": false,
    "salesDownPayment": false,
    "onlineOrderId": null,
    "approvalTypeNumberId": null,
    "purchaseReturn": false,
    "onlineOrder": null,
    "totalDownPaymentUsed": 0.0,
    "canProcessToPurchaseOrder": true,
    "totalExpense": 106875.0,
    "percentShipped": 100.0,
    "inclusiveTax": true,
    "stockOpnameResult": false,
    "taxableDiscount4": 0.0,
    "exchangeInvoice": false,
    "taxableDiscount2": 0.0,
    "subTotal": 537600.0,
    "lastCashDiscount": 0.0,
    "taxableDiscount1": 0.0,
    "toAddress": "Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Parang Kode pos 90157",
    "rollOver": false,
    "paymentPointOnlineBank": false,
    "employeeLoanDisbursement": false,
    "manufactureOrder": false,
    "totalReturnDownPayment": 0.0,
    "tax2Rate": 0.0,
    "itemAdjustment": false,
    "finishedProject": false,
    "closeReason": null,
    "forceCalculatePercentTaxable": false,
    "periodEnd": false,
    "workOrder": false,
    "masterSalesmanId": 350,
    "purchaseDownPayment": false,
    "shipment": {
      "shipAddressStreet": null,
      "optLock": 1,
      "shipAddressZipCode": null,
      "shipAddressCountry": null,
      "name": "SPX STANDARD",
      "shipAddressCity": null,
      "picPhoneNumber": null,
      "shipAddressProvince": null,
      "picName": null,
      "id": 351,
      "suspended": false,
      "shipAddress": ""
    },
    "canProcess": false,
    "assetTransfer": false,
    "recurringDetailId": null,
    "stockOpnameOrder": false,
    "dpUsedHistory": [],
    "salesCheckIn": false,
    "totalAmount": 644475.0,
    "downPayments": [],
    "shipDateView": "17 Mar 2026",
    "salesQuotation": false,
    "fixedAssetEdited": false,
    "manualApprovalNumber": null,
    "fob": null,
    "purchaseRequisition": false,
    "paymentTerm": {
      "cashOnDelivery": false,
      "optLock": 0,
      "installmentTerm": false,
      "discDays": 0,
      "name": "net 14",
      "defaultTerm": true,
      "memo": null,
      "discPC": 0.0,
      "id": 1800,
      "netDays": 14,
      "suspended": false,
      "manualTerm": false
    },
    "dppAmount": 484324.0,
    "finishedGoodSlip": false,
    "tax2Amount": 0.0,
    "purchasePayment": false,
    "description": "(TRF-NURA) SPX 106.875 VP40(4) ANDI MARUF\n\nFREE VP10(1)",
    "otherDeposit": false,
    "otherPayment": false,
    "tax1": {
      "pphPs4Type": null,
      "purchaseTaxGlAccountId": 75,
      "pph23Type": null,
      "optLock": 1,
      "description": "Pajak Pertambahan Nilai",
      "pph15Type": null,
      "taxCode": "PPN",
      "taxInfo": "PPN 11%",
      "pph22Type": null,
      "rate": 11.0,
      "salesTaxGlAccountId": 74,
      "id": 50,
      "taxType": "PPN"
    },
    "availableInputDownPayment": 537600.0,
    "costDistribution": false,
    "tax2": null,
    "manualClosedVisible": false,
    "budgetPlan": false,
    "itemTransfer": false,
    "vendorClaim": false,
    "rate": 1.0,
    "forceCalculateTaxRate": false,
    "transDate": "17/03/2026",
    "manualClosed": false,
    "cashDiscount": 0.0,
    "salesReceipt": false,
    "tax3Amount": 0.0,
    "materialEquipment": false,
    "tax4": null,
    "approvalStatus": "APPROVED",
    "cashDiscPercent": "",
    "tax2Id": null,
    "attachmentExist": false,
    "materialSlip": false,
    "autoCloseVisible": false,
    "sellingPriceAdjustment": false,
    "materialAdjustment": false,
    "totalDownPayment": 0.0,
    "autoCloseRange": 0,
    "numericField9": 0.0,
    "checkInId": null,
    "numericField8": 0.0,
    "numericField7": 0.0,
    "createdBy": 307470,
    "shipmentId": 351,
    "numericField6": 0.0,
    "numericField5": 0.0,
    "numericField4": 0.0,
    "purchaseOrder": false,
    "numericField3": 0.0,
    "fixedAsset": false,
    "numericField2": 0.0,
    "attachmentCount": 0,
    "numericField1": 0.0,
    "standardProductCost": false,
    "userPrinted": null,
    "customer": {
      "documentCode": "DIGUNGGUNG",
      "consignmentStore": false,
      "salesAccountId": null,
      "referenceCustomerLimitId": null,
      "charField8": null,
      "customerLimitAmountValue": 0.0,
      "charField9": null,
      "charField6": null,
      "contactInfo": {
        "branchId": null,
        "website": null,
        "notes": null,
        "homePhone": null,
        "companyName": "Andi Ma'ruf",
        "optLock": 0,
        "project": false,
        "mobilePhone": "085374325349",
        "vendor": false,
        "customerId": 78213,
        "name": "Andi Ma'ruf",
        "bbmPin": null,
        "salesman": false,
        "workPhone": "085374325349",
        "salutation": null,
        "position": null,
        "id": 78863,
        "fax": null,
        "email": null,
        "seq": null,
        "customer": true
      },
      "charField7": null,
      "numericField10": 0.0,
      "idCard": null,
      "charField4": null,
      "charField5": null,
      "optLock": 1,
      "customerLimitAge": false,
      "salesReturnAccountId": null,
      "defaultIncTax": true,
      "groupCustomerLimit": false,
      "charField2": null,
      "charField3": null,
      "charField1": null,
      "id": 78213,
      "costOfGoodsSoldAccountId": null,
      "salesman3Id": null,
      "currencyId": 50,
      "customerSalesDiscountAccountId": null,
      "arAccountCount": 0,
      "salesman5Id": null,
      "dateField2": null,
      "branchId": null,
      "wpNumber": null,
      "shipSameAsBill": true,
      "dateField1": null,
      "defaultTermId": 1800,
      "pkpNo": null,
      "npwpNo": null,
      "warehouse": null,
      "documentTransaction": "CTAS_DIPERSAMAKAN",
      "suspended": false,
      "warehouseId": null,
      "name": "Andi Ma'ruf",
      "shipAddressList": [
        {
          "country": "",
          "zipCode": "",
          "notes": "Andi Ma'ruf",
          "city": "",
          "latitude": null,
          "optLock": 2,
          "vendorId": null,
          "picMobileNo": "085374325349",
          "picName": "Andi Ma'ruf",
          "province": "",
          "street": "Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Parang Kode pos 90157",
          "customerId": 78213,
          "concatFullAddress": "Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Parang Kode pos 90157",
          "id": 79963,
          "longitude": null,
          "branchId": null,
          "address": "Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Parang Kode pos 90157",
          "locationLabel": null,
          "employeeId": null,
          "suspended": false,
          "taxLocation": true,
          "deleted": false,
          "warehouseId": null,
          "name": "Andi Ma'ruf",
          "isOtherAddress": false,
          "projectId": null,
          "defaultLocation": false,
          "headQuarter": false
        }
      ],
      "salesman": null,
      "defaultInvoiceDesc": null,
      "charField10": null,
      "notesIdTax": null,
      "salesDiscountAccountId": null,
      "dpAccountCount": 0,
      "wpType": "NIK",
      "customerSalesReturnAccountId": null,
      "countryCode": "IDN",
      "customerSalesAccountId": null,
      "shipAddressId": 79963,
      "wpName": null,
      "customerTaxType": "CTAS_KEPADA_SELAIN_PEMUNGUT_PPN",
      "itemDiscountAccountId": null,
      "salesman4Id": null,
      "taxSameAsBill": true,
      "wpTypeAndNumber": "-",
      "customerLimitAgeValue": 0,
      "taxAddressId": 79963,
      "attachmentExist": false,
      "customerItemDiscountAccountId": null,
      "customerCostOfGoodsSoldAccountId": null,
      "salesman2Id": null,
      "priceCategoryId": 151,
      "defaultSalesmanId": null,
      "billAddressId": 79963,
      "defaultWarehouseId": null,
      "reseller": false,
      "customerNoVa": null,
      "shipAddress": {
        "country": "",
        "zipCode": "",
        "notes": "Andi Ma'ruf",
        "city": "",
        "latitude": null,
        "optLock": 2,
        "vendorId": null,
        "picMobileNo": "085374325349",
        "picName": "Andi Ma'ruf",
        "province": "",
        "street": "Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Parang Kode pos 90157",
        "customerId": 78213,
        "concatFullAddress": "Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Parang Kode pos 90157",
        "id": 79963,
        "longitude": null,
        "branchId": null,
        "address": "Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Parang Kode pos 90157",
        "locationLabel": null,
        "employeeId": null,
        "suspended": false,
        "taxLocation": true,
        "deleted": false,
        "warehouseId": null,
        "name": "Andi Ma'ruf",
        "isOtherAddress": false,
        "projectId": null,
        "defaultLocation": false,
        "headQuarter": false
      },
      "numericField9": 0.0,
      "defaultSalesDisc": null,
      "numericField8": 0.0,
      "numericField7": 0.0,
      "numericField6": 0.0,
      "numericField5": 0.0,
      "numericField4": 0.0,
      "efakturSendEmail": null,
      "numericField3": 0.0,
      "numericField2": 0.0,
      "numericField1": 0.0,
      "nitku": null,
      "categoryId": 2050,
      "customerNo": "CUST.05784",
      "discountCategoryId": 50,
      "customerLimitAmount": false
    }
  }
}

============================================================
STRUCTURE TREE
============================================================
s: bool  = True
d:
  printUserName: str   = 'Belum cetak/email'
  charField8: str   = ''
  charField9: str   = ''
  tax4Amount: float = 0.0
  charField6: str   = ''
  tax1Rate: float = 11.0
  charField7: str   = ''
  numericField10: float = 0.0
  charField4: str   = ''
  foodDelivery: bool  = False
  charField5: str   = ''
  optLock: int   = 8
  percentTaxable: float = 100.0
  receiveItem: bool  = False
  number: str   = 'SO.0326-651'
  printedTime: null
  processHistory: list[2]
    [0]:
      approvalStatus: str   = 'APPROVED'
      historyDate: str   = '17/03/2026'
      historyNumber: str   = 'DO.0326.666'
      historyType: str   = 'DO'
      index: int   = 0
      id: int   = 77087
  downPaymentHistory: list[0]
  charField2: str   = ''
  charField3: str   = ''
  charField1: str   = ''
  id: int   = 82994
  currencyId: int   = 50
  transDateView: str   = '17 Mar 2026'
  hasStatusHistory: bool  = True
  dateField2: null
  branchId: int   = 50
  tax1Id: int   = 50
  dateField1: null
  materialAllocation: bool  = False
  taxable: bool  = True
  salesInvoice: bool  = False
  billOfMaterial: bool  = False
  employeeLoanSettlement: bool  = False
  purchaseInvoice: bool  = False
  shipDate: str   = '17/03/2026'
  tax1Amount: float = 53276.0
  salesOrder: bool  = True
  commentCount: int   = 0
  transferOrder: bool  = False
  detailExpense: list[1]
    [0]:
      salesOrderId: int   = 82994
      dataClassification10: null
      detailName: str   = 'B. Transport Barang - Bintaro'
      departmentId: null
      optLock: int   = 0
      project: null
      expenseName: str   = 'B. Transport Barang - Bintaro'
      expenseAmount: float = 106875.0
      dataClassification10Id: null
      dataClassification9Id: null
      id: int   = 63410
      dataClassification8Id: null
      department: null
      dataClassification7Id: null
      salesQuotationId: null
      dataClassification6Id: null
      seq: int   = 1
      dataClassification5Id: null
      dataClassification4Id: null
      dataClassification1: null
      dataClassification3Id: null
      dataClassification2Id: null
      amount: float = 106875.0
      dataClassification3: null
      dataClassification1Id: null
      dataClassification2: null
      dataClassification5: null
      dataClassification4: null
      dataClassification7: null
      dataClassification6: null
      dataClassification9: null
      dataClassification8: null
      salesOrder:
        number: str   = 'SO.0326-651'
        id: int   = 82994
      accountId: int   = 461
      expenseNotes: null
      projectId: null
      account:
        no: str   = '56102.02'
        sub: bool  = True
        parent: dict  keys=['no', 'sub', 'parent', 'lvl', 'accountType', 'optLock', 'memo', 'accountTypeName', 'nameWithIndent', 'parentNode', 'suspended', 'autoNumberTransactionId', 'nameWithIndentStrip', 'fiscal', 'noWithIndent', 'name', 'id', 'currencyId']
        lvl: int   = 3
        accountType: str   = 'EXPENSE'
        optLock: int   = 1
        memo: null
        accountTypeName: str   = 'Beban'
        nameWithIndent: str   = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;B. Transport' …
        parentNode: bool  = False
        suspended: bool  = False
        autoNumberTransactionId: null
        nameWithIndentStrip: str   = '- - B. Transport Barang - Bintaro'
        fiscal: bool  = False
        noWithIndent: str   = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;56102.02'
        name: str   = 'B. Transport Barang - Bintaro'
        id: int   = 461
        currencyId: int   = 50
  hasNPWP: bool  = True
  detailItem: list[1]
    [0]:
      lastItemDiscPercent: str   = ''
      charField8: null
      charField9: null
      processQuantityDesc: str   = '4 VP'
      charField6: null
      charField7: null
      numericField10: float = 0.0
      charField4: null
      departmentId: null
      charField5: null
      optLock: int   = 21
      itemUnit:
        codeUnitTax: null
        optLock: int   = 0
        name: str   = 'VP'
        id: int   = 1000
      salesOrderPoNumber: null
      availableUnitRatio: float = 1.0
      defaultWarehouseDeliveryOrder:
        scrapWarehouse: bool  = False
        defaultWarehouse: bool  = False
        locationId: int   = 805
        optLock: int   = 5
        name: str   = 'Gudang Bogor (FG)'
        description: str   = 'Pencatatan lokasi Barang Jadi di Bogor'
        pic: null
        id: int   = 300
        suspended: bool  = False
      charField2: null
      charField3: null
      charField1: null
      id: int   = 92569
      salesman3Id: null
      discountRule: list[2]
        [0]:
          minQuantity: int   = 0
          spaId: null
          transDate: str   = '2026-03-28'
          discountFromSpa: bool  = False
          unitId: int   = 1000
          discount: str   = ''
      dataClassification6Id: null
      salesQuotationDetailId: null
      unitPrice: float = 134400.0
      useTax1: bool  = True
      dateField2: null
      dataClassification1: null
      salesmanName: str   = 'Siti Nurani'
      branchId: int   = 50
      useTax3: bool  = False
      item:
        unit2Id: int   = 3000
        charField8: null
        charField9: null
        charField6: null
        charField7: null
        numericField10: null
        unit4Price: float = 0.0
        charField4: null
        charField5: null
        optLock: int   = 49
        percentTaxable: float = 100.0
        itemBrandId: null
        ratioVendorUnit: float = 1.0
        unit3Price: float = 0.0
        salesDiscountGlAccountId: int   = 1007
        itemProduced: bool  = False
        charField2: null
        charField3: null
        charField1: null
        id: int   = 613
        maxOptionModifier: null
        unitPrice: float = 134400.0
        dateField2: null
        branchId: null
        tax1Id: int   = 50
        dateField1: null
        onSales: float = 0.0
        useWholesalePrice: bool  = False
        unit5Price: float = 0.0
        unit2Price: float = 672000.0
        suspended: bool  = False
        goodTransitGlAccountId: int   = 117
        cogsGlAccountId: int   = 178
        referenceSubstitutionId: null
        itemSubstitutionId: null
        shortName: str   = 'Alanabi Value Pack'
        charField10: null
        unBilledGlAccountId: int   = 151
        canChangeDetailGroup: bool  = False
        variantLabel2: null
        dimWidth: float = 0.0
        variantLabel1: null
        unit3Id: null
        salesRetGlAccountId: int   = 1004
        dimDepth: float = 0.0
        minimumQuantityReorder: float = 0.0
        lockTime: null
        vendorPrice: float = 0.0
        minimumQuantity: float = 0.0
        tax4Id: null
        dimHeight: float = 0.0
        additionalCost: bool  = False
        unit4Id: null
        notes: null
        purchaseRetGlAccountId: int   = 800
        unit1: dict  keys=['codeUnitTax', 'optLock', 'name', 'id']
        variantParentId: null
        unit2: dict  keys=['codeUnitTax', 'optLock', 'name', 'id']
        unit3: null
        vendorUnit: dict  keys=['codeUnitTax', 'optLock', 'name', 'id']
        preferedVendorId: null
        ratio2: float = 5.0
        unit4: null
        unit5: null
        ratio4: float = 0.0
        ratio3: float = 0.0
        ratio5: float = 0.0
        variantDetail2: null
        tax3Id: null
        variantDetail1: null
        inventoryGlAccountId: int   = 800
        weight: null
        controlQuantity: bool  = False
        upcNo: null
        substituted: bool  = False
        minOptionModifier: float = 1.0
        salesGlAccountId: int   = 164
        name: str   = 'Alanabi Value Pack 40 PCS'
        deliveryLeadTime: float = 0.0
        manageExpired: bool  = True
        no: str   = 'FG-VP40PCS-00'
        defaultDiscount: null
        itemType: str   = 'INVENTORY'
        unit1Id: int   = 1000
        unit5Id: null
        itemCategoryId: int   = 151
        hasImage: bool  = False
        tax1: dict  keys=['pphPs4Type', 'purchaseTaxGlAccountId', 'pph23Type', 'optLock', 'description', 'pph15Type', 'taxCode', 'taxInfo', 'pph22Type', 'rate', 'salesTaxGlAccountId', 'id', 'taxType']
        tax2: null
        manageSN: bool  = False
        materialProduced: bool  = False
        variantSeq: null
        codeItemTax: null
        tax3: null
        tax4: null
        serialNumberType: str   = 'BATCH'
        tax2Id: null
        cost: float = 0.0
        printDetailGroup: bool  = False
        calculateGroupPrice: bool  = False
        numericField9: null
        defStandardCost: float = 0.0
        numericField8: null
        minimumSellingQuantity: float = 0.0
        numericField7: null
        numericField6: null
        numericField5: null
        numericField4: null
        numericField3: null
        numericField2: null
        numericField1: null
        vendorUnitId: int   = 1000
        unit1Price: float = 134400.0
      dataClassification3: null
      dataClassification1Id: null
      useTax2: bool  = False
      dateField1: null
      dataClassification2: null
      dataClassification5: null
      dataClassification4: null
      availableItemUnitName: str   = 'VP'
      dataClassification7: null
      dataClassification6: null
      dataClassification9: null
      dataClassification8: null
      tax1Amount: float = 53275.675676
      detailNotes: null
      warehouse:
        scrapWarehouse: bool  = False
        defaultWarehouse: bool  = False
        locationId: int   = 805
        optLock: int   = 5
        name: str   = 'Gudang Bogor (FG)'
        description: str   = 'Pencatatan lokasi Barang Jadi di Bogor'
        pic: null
        id: int   = 300
        suspended: bool  = False
      salesOrder:
        number: str   = 'SO.0326-651'
        taxable: bool  = True
        inclusiveTax: bool  = True
        id: int   = 82994
      itemId: int   = 613
      warehouseId: int   = 300
      charField15: null
      charField13: null
      charField14: null
      charField11: null
      charField12: null
      useTax4: bool  = False
      charField10: null
      canChangeDetailGroup: bool  = False
      dataClassification10: null
      detailName: str   = 'Alanabi Value Pack 40 PCS'
      lastItemCashDiscount: float = 0.0
      totalPrice: float = 537600.0
      groupSeq: null
      transferQuantity: float = 0.0
      salesAmount: float = 484324.324324
      dataClassification7Id: null
      seq: int   = 1
      availableQuantity: float = 0.0
      dataClassification2Id: null
      salesman2Id: null
      onlineOrderDetailId: null
      onlineOrderId: null
      closed: bool  = True
      onlineOrder: null
      salesOrderId: int   = 82994
      onlineOrderDetail: null
      project: null
      quantityDefault: float = 4.0
      itemDiscPercent: str   = ''
      dataClassification8Id: null
      salesQuotationId: null
      salesman5Id: null
      availableItemCashDiscount: float = 0.0
      dataClassification3Id: null
      salesman1Id: int   = 350
      tax3Id: null
      availableUnitPrice: float = 134400.0
      grossAmount: float = 484324.324324
      poQuantity: float = 0.0
      projectId: null
      dppAmount: float = 484324.324324
      tax2Amount: float = 0.0
      unitPriceRule: list[2]
        [0]:
          minQuantity: float = 0.0
          price: float = 134400.0
          spaId: int   = 2951
          unitId: int   = 1000
          priceFromSpa: bool  = True
          minimumPrice: float = 0.0
      availableTotalPrice: float = 537600.0
      manualClosedVisible: bool  = False
      dataClassification10Id: null
      itemCashDiscount: float = 0.0
      dataClassification9Id: null
      salesmanList: list[1]
        [0]:
          resignMonth: null
          departmentId: null
          optLock: int   = 5
          joinDateView: str   = '28 Apr 2022'
          resignYear: null
          contactInfoId: int   = 2609
          bankName: str   = 'BANK CIMB NIAGA'
          startMonthPayment: int   = 5
          nikNo: str   = '3202075608970003'
          addressId: int   = 3010
          number: str   = 'BAN016'
          joinDate: str   = '28/04/2022'
          salesmanUserId: null
          nettoIncomeBefore: float = 0.0
          id: int   = 350
          pphBefore: float = 0.0
          posRoleId: int   = 51
          startYearPayment: int   = 2022
          employeeTaxStatus: str   = 'TK0'
          bankAccount: str   = '762755768800'
          bankAccountName: str   = 'Siti Nurani'
          domisiliType: str   = 'INA'
          branchId: int   = 50
          bankCode: str   = '022'
          attachmentExist: bool  = False
          calculatePtkp: bool  = True
          pph: bool  = False
          npwpNo: null
          suspended: bool  = False
          employeeWorkStatus: str   = 'PEGAWAI_TETAP'
          name: str   = 'Siti Nurani'
          salesman: bool  = True
          resign: bool  = False
      manualClosed: bool  = False
      department: null
      salesman4Id: null
      tax3: null
      detailTaxName: str   = 'PPN 11%'
      dataClassification5Id: null
      dataClassification4Id: null
      quantity: float = 4.0
      defaultWarehouseSalesInvoice:
        scrapWarehouse: bool  = False
        defaultWarehouse: bool  = False
        locationId: int   = 805
        optLock: int   = 5
        name: str   = 'Gudang Bogor (FG)'
        description: str   = 'Pencatatan lokasi Barang Jadi di Bogor'
        pic: null
        id: int   = 300
        suspended: bool  = False
      manufactureOrderDetailId: null
      shipQuantity: float = 4.0
      numericField9: float = 0.0
      numericField8: float = 0.0
      numericField7: float = 0.0
      numericField6: float = 0.0
      numericField5: float = 0.0
      numericField4: float = 0.0
      itemUnitId: int   = 1000
      numericField3: float = 0.0
      numericField2: float = 0.0
      numericField1: float = 0.0
      availableItemUnit:
        codeUnitTax: null
        optLock: int   = 0
        name: str   = 'VP'
        id: int   = 1000
      unitRatio: float = 1.0
  employeePayment: bool  = False
  taxableAmount2: float = 0.0
  expenseAccrual: bool  = False
  taxableAmount1: float = 484324.324324
  salesReturn: bool  = False
  lastCashDiscPercent: str   = ''
  taxableAmount4: float = 0.0
  poNumber: null
  charField10: str   = ''
  status: str   = 'PROCEED'
  processStages: bool  = False
  employeeLoanInstallment: bool  = False
  bankTransfer: bool  = False
  preliminarySurvey: bool  = False
  employeeLoan: bool  = False
  availableDownPayment: float = 0.0
  jobOrder: bool  = False
  customerClaim: bool  = False
  journal: bool  = False
  salesAmount: float = 484324.324324
  deliveryPacking: bool  = False
  customerId: int   = 78213
  percentTaxablePrecision: float = 100.0
  statusName: str   = 'Terproses'
  currency:
    defaultArAccountId: int   = 108
    symbol: str   = 'Rp'
    code: str   = 'IDR'
    defaultSalesDiscAccountId: int   = 1007
    optLock: int   = 10
    currencyConverterType: str   = 'TO_LOCAL'
    defaultAdvSalesAccountId: int   = 59
    exchangeRateSymbolCode: str   = 'Rp'
    defaultAdvPurchaseAccountId: int   = 58
    defaultRealizeGlAccountId: int   = 550
    name: str   = 'Indonesian Rupiah'
    codeSymbol: str   = 'IDR Rp'
    id: int   = 50
    defaultApAccountId: int   = 56
    defaultUnrealizeGlAccountId: int   = 551
    converterTypeName: str   = '1 IDR=XXX IDR'
  vendorPrice: bool  = False
  paymentTermId: int   = 1800
  tax4Rate: float = 0.0
  tax4Id: null
  fobId: null
  autoCloseChecked: bool  = False
  deliveryOrder: bool  = False
  salesDownPayment: bool  = False
  onlineOrderId: null
  approvalTypeNumberId: null
  purchaseReturn: bool  = False
  onlineOrder: null
  totalDownPaymentUsed: float = 0.0
  canProcessToPurchaseOrder: bool  = True
  totalExpense: float = 106875.0
  percentShipped: float = 100.0
  inclusiveTax: bool  = True
  stockOpnameResult: bool  = False
  taxableDiscount4: float = 0.0
  exchangeInvoice: bool  = False
  taxableDiscount2: float = 0.0
  subTotal: float = 537600.0
  lastCashDiscount: float = 0.0
  taxableDiscount1: float = 0.0
  toAddress: str   = 'Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Par' …
  rollOver: bool  = False
  paymentPointOnlineBank: bool  = False
  employeeLoanDisbursement: bool  = False
  manufactureOrder: bool  = False
  totalReturnDownPayment: float = 0.0
  tax2Rate: float = 0.0
  itemAdjustment: bool  = False
  finishedProject: bool  = False
  closeReason: null
  forceCalculatePercentTaxable: bool  = False
  periodEnd: bool  = False
  workOrder: bool  = False
  masterSalesmanId: int   = 350
  purchaseDownPayment: bool  = False
  shipment:
    shipAddressStreet: null
    optLock: int   = 1
    shipAddressZipCode: null
    shipAddressCountry: null
    name: str   = 'SPX STANDARD'
    shipAddressCity: null
    picPhoneNumber: null
    shipAddressProvince: null
    picName: null
    id: int   = 351
    suspended: bool  = False
    shipAddress: str   = ''
  canProcess: bool  = False
  assetTransfer: bool  = False
  recurringDetailId: null
  stockOpnameOrder: bool  = False
  dpUsedHistory: list[0]
  salesCheckIn: bool  = False
  totalAmount: float = 644475.0
  downPayments: list[0]
  shipDateView: str   = '17 Mar 2026'
  salesQuotation: bool  = False
  fixedAssetEdited: bool  = False
  manualApprovalNumber: null
  fob: null
  purchaseRequisition: bool  = False
  paymentTerm:
    cashOnDelivery: bool  = False
    optLock: int   = 0
    installmentTerm: bool  = False
    discDays: int   = 0
    name: str   = 'net 14'
    defaultTerm: bool  = True
    memo: null
    discPC: float = 0.0
    id: int   = 1800
    netDays: int   = 14
    suspended: bool  = False
    manualTerm: bool  = False
  dppAmount: float = 484324.0
  finishedGoodSlip: bool  = False
  tax2Amount: float = 0.0
  purchasePayment: bool  = False
  description: str   = '(TRF-NURA) SPX 106.875 VP40(4) ANDI MARUF\n\nFREE VP10(1)'
  otherDeposit: bool  = False
  otherPayment: bool  = False
  tax1:
    pphPs4Type: null
    purchaseTaxGlAccountId: int   = 75
    pph23Type: null
    optLock: int   = 1
    description: str   = 'Pajak Pertambahan Nilai'
    pph15Type: null
    taxCode: str   = 'PPN'
    taxInfo: str   = 'PPN 11%'
    pph22Type: null
    rate: float = 11.0
    salesTaxGlAccountId: int   = 74
    id: int   = 50
    taxType: str   = 'PPN'
  availableInputDownPayment: float = 537600.0
  costDistribution: bool  = False
  tax2: null
  manualClosedVisible: bool  = False
  budgetPlan: bool  = False
  itemTransfer: bool  = False
  vendorClaim: bool  = False
  rate: float = 1.0
  forceCalculateTaxRate: bool  = False
  transDate: str   = '17/03/2026'
  manualClosed: bool  = False
  cashDiscount: float = 0.0
  salesReceipt: bool  = False
  tax3Amount: float = 0.0
  materialEquipment: bool  = False
  tax4: null
  approvalStatus: str   = 'APPROVED'
  cashDiscPercent: str   = ''
  tax2Id: null
  attachmentExist: bool  = False
  materialSlip: bool  = False
  autoCloseVisible: bool  = False
  sellingPriceAdjustment: bool  = False
  materialAdjustment: bool  = False
  totalDownPayment: float = 0.0
  autoCloseRange: int   = 0
  numericField9: float = 0.0
  checkInId: null
  numericField8: float = 0.0
  numericField7: float = 0.0
  createdBy: int   = 307470
  shipmentId: int   = 351
  numericField6: float = 0.0
  numericField5: float = 0.0
  numericField4: float = 0.0
  purchaseOrder: bool  = False
  numericField3: float = 0.0
  fixedAsset: bool  = False
  numericField2: float = 0.0
  attachmentCount: int   = 0
  numericField1: float = 0.0
  standardProductCost: bool  = False
  userPrinted: null
  customer:
    documentCode: str   = 'DIGUNGGUNG'
    consignmentStore: bool  = False
    salesAccountId: null
    referenceCustomerLimitId: null
    charField8: null
    customerLimitAmountValue: float = 0.0
    charField9: null
    charField6: null
    contactInfo:
      branchId: null
      website: null
      notes: null
      homePhone: null
      companyName: str   = "Andi Ma'ruf"
      optLock: int   = 0
      project: bool  = False
      mobilePhone: str   = '085374325349'
      vendor: bool  = False
      customerId: int   = 78213
      name: str   = "Andi Ma'ruf"
      bbmPin: null
      salesman: bool  = False
      workPhone: str   = '085374325349'
      salutation: null
      position: null
      id: int   = 78863
      fax: null
      email: null
      seq: null
      customer: bool  = True
    charField7: null
    numericField10: float = 0.0
    idCard: null
    charField4: null
    charField5: null
    optLock: int   = 1
    customerLimitAge: bool  = False
    salesReturnAccountId: null
    defaultIncTax: bool  = True
    groupCustomerLimit: bool  = False
    charField2: null
    charField3: null
    charField1: null
    id: int   = 78213
    costOfGoodsSoldAccountId: null
    salesman3Id: null
    currencyId: int   = 50
    customerSalesDiscountAccountId: null
    arAccountCount: int   = 0
    salesman5Id: null
    dateField2: null
    branchId: null
    wpNumber: null
    shipSameAsBill: bool  = True
    dateField1: null
    defaultTermId: int   = 1800
    pkpNo: null
    npwpNo: null
    warehouse: null
    documentTransaction: str   = 'CTAS_DIPERSAMAKAN'
    suspended: bool  = False
    warehouseId: null
    name: str   = "Andi Ma'ruf"
    shipAddressList: list[1]
      [0]:
        country: str   = ''
        zipCode: str   = ''
        notes: str   = "Andi Ma'ruf"
        city: str   = ''
        latitude: null
        optLock: int   = 2
        vendorId: null
        picMobileNo: str   = '085374325349'
        picName: str   = "Andi Ma'ruf"
        province: str   = ''
        street: str   = 'Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Par' …
        customerId: int   = 78213
        concatFullAddress: str   = 'Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Par' …
        id: int   = 79963
        longitude: null
        branchId: null
        address: str   = 'Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Par' …
        locationLabel: null
        employeeId: null
        suspended: bool  = False
        taxLocation: bool  = True
        deleted: bool  = False
        warehouseId: null
        name: str   = "Andi Ma'ruf"
        isOtherAddress: bool  = False
        projectId: null
        defaultLocation: bool  = False
        headQuarter: bool  = False
    salesman: null
    defaultInvoiceDesc: null
    charField10: null
    notesIdTax: null
    salesDiscountAccountId: null
    dpAccountCount: int   = 0
    wpType: str   = 'NIK'
    customerSalesReturnAccountId: null
    countryCode: str   = 'IDN'
    customerSalesAccountId: null
    shipAddressId: int   = 79963
    wpName: null
    customerTaxType: str   = 'CTAS_KEPADA_SELAIN_PEMUNGUT_PPN'
    itemDiscountAccountId: null
    salesman4Id: null
    taxSameAsBill: bool  = True
    wpTypeAndNumber: str   = '-'
    customerLimitAgeValue: int   = 0
    taxAddressId: int   = 79963
    attachmentExist: bool  = False
    customerItemDiscountAccountId: null
    customerCostOfGoodsSoldAccountId: null
    salesman2Id: null
    priceCategoryId: int   = 151
    defaultSalesmanId: null
    billAddressId: int   = 79963
    defaultWarehouseId: null
    reseller: bool  = False
    customerNoVa: null
    shipAddress:
      country: str   = ''
      zipCode: str   = ''
      notes: str   = "Andi Ma'ruf"
      city: str   = ''
      latitude: null
      optLock: int   = 2
      vendorId: null
      picMobileNo: str   = '085374325349'
      picName: str   = "Andi Ma'ruf"
      province: str   = ''
      street: str   = 'Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Par' …
      customerId: int   = 78213
      concatFullAddress: str   = 'Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Par' …
      id: int   = 79963
      longitude: null
      branchId: null
      address: str   = 'Makassar , jl.Pajenekang 59 Kec.Bontoala , kel. Bontoala Par' …
      locationLabel: null
      employeeId: null
      suspended: bool  = False
      taxLocation: bool  = True
      deleted: bool  = False
      warehouseId: null
      name: str   = "Andi Ma'ruf"
      isOtherAddress: bool  = False
      projectId: null
      defaultLocation: bool  = False
      headQuarter: bool  = False
    numericField9: float = 0.0
    defaultSalesDisc: null
    numericField8: float = 0.0
    numericField7: float = 0.0
    numericField6: float = 0.0
    numericField5: float = 0.0
    numericField4: float = 0.0
    efakturSendEmail: null
    numericField3: float = 0.0
    numericField2: float = 0.0
    numericField1: float = 0.0
    nitku: null
    categoryId: int   = 2050
    customerNo: str   = 'CUST.05784'
    discountCategoryId: int   = 50
    customerLimitAmount: bool  = False
