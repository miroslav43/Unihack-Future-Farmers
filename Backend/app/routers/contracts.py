from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.contract import (
    ContractCreate, 
    ContractResponse, 
    SignContractRequest,
    KeyPairResponse
)
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User, FarmerProfile, BuyerProfile
from app.models.contract import Contract, ContractStatus
from app.services.contract_service import generate_contract_hash, generate_keys
from datetime import datetime
from typing import List, Optional
from uuid import UUID

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("/", response_model=ContractResponse)
async def create_contract(
    contract_data: ContractCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new contract (buyer only)"""
    # Verify user is a buyer
    if current_user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can create contracts"
        )
    
    # Verify buyer owns the buyer_id in the contract
    result = await db.execute(
        select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
    )
    buyer_profile = result.scalar_one_or_none()
    
    if not buyer_profile or buyer_profile.id != UUID(contract_data.buyer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create contract for another buyer"
        )
    
    # Verify farmer exists
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.id == UUID(contract_data.farmer_id))
    )
    farmer = result.scalar_one_or_none()
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Prepare contract data for hashing
    contract_dict = contract_data.model_dump()
    
    # Generate contract hash
    hash_data = {
        "buyer_id": contract_dict["buyer_id"],
        "farmer_id": contract_dict["farmer_id"],
        "items": contract_dict["items"],
        "total_amount": contract_dict["total_amount"],
        "delivery_date": contract_dict.get("delivery_date"),
        "delivery_address": contract_dict.get("delivery_address"),
        "terms": contract_dict.get("terms")
    }
    contract_hash = generate_contract_hash(hash_data)
    
    # Create contract
    contract = Contract(
        buyer_id=UUID(contract_data.buyer_id),
        buyer_name=contract_data.buyer_name,
        farmer_id=UUID(contract_data.farmer_id),
        farmer_name=contract_data.farmer_name,
        items=[item.model_dump() for item in contract_data.items],
        total_amount=contract_data.total_amount,
        delivery_date=contract_data.delivery_date,
        delivery_address=contract_data.delivery_address,
        terms=contract_data.terms,
        notes=contract_data.notes,
        status=ContractStatus.PENDING.value,
        contract_hash=contract_hash
    )
    
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    
    return ContractResponse(
        _id=str(contract.id),
        buyer_id=str(contract.buyer_id),
        buyer_name=contract.buyer_name,
        farmer_id=str(contract.farmer_id),
        farmer_name=contract.farmer_name,
        items=[item for item in contract.items],
        total_amount=contract.total_amount,
        delivery_date=contract.delivery_date,
        delivery_address=contract.delivery_address,
        terms=contract.terms,
        notes=contract.notes,
        status=contract.status,
        contract_hash=contract.contract_hash,
        blockchain_tx_id=contract.blockchain_tx_id,
        farmer_signature=contract.farmer_signature,
        buyer_signature=contract.buyer_signature,
        created_at=contract.created_at,
        updated_at=contract.updated_at,
        signed_at=contract.signed_at,
        completed_at=contract.completed_at
    )


@router.get("/", response_model=List[ContractResponse])
async def get_contracts(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contracts for current user (filtered by role)"""
    # Build query based on user role
    if current_user.role == "farmer":
        # Get farmer profile
        result = await db.execute(
            select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
        )
        farmer = result.scalar_one_or_none()
        if not farmer:
            return []
        query = select(Contract).where(Contract.farmer_id == farmer.id)
    elif current_user.role == "buyer":
        # Get buyer profile
        result = await db.execute(
            select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
        )
        buyer = result.scalar_one_or_none()
        if not buyer:
            return []
        query = select(Contract).where(Contract.buyer_id == buyer.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role"
        )
    
    # Add status filter if provided
    if status_filter:
        query = query.where(Contract.status == status_filter)
    
    query = query.order_by(Contract.created_at.desc())
    result = await db.execute(query)
    contracts = result.scalars().all()
    
    return [
        ContractResponse(
            _id=str(contract.id),
            buyer_id=str(contract.buyer_id),
            buyer_name=contract.buyer_name,
            farmer_id=str(contract.farmer_id),
            farmer_name=contract.farmer_name,
            items=contract.items,
            total_amount=contract.total_amount,
            delivery_date=contract.delivery_date,
            delivery_address=contract.delivery_address,
            terms=contract.terms,
            notes=contract.notes,
            status=contract.status,
            contract_hash=contract.contract_hash,
            blockchain_tx_id=contract.blockchain_tx_id,
            farmer_signature=contract.farmer_signature,
            buyer_signature=contract.buyer_signature,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
            signed_at=contract.signed_at,
            completed_at=contract.completed_at
        )
        for contract in contracts
    ]


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract_by_id(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get contract by ID (ownership check)"""
    result = await db.execute(
        select(Contract).where(Contract.id == UUID(contract_id))
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Verify user has access to this contract
    if current_user.role == "farmer":
        result = await db.execute(
            select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
        )
        farmer = result.scalar_one_or_none()
        if not farmer or contract.farmer_id != farmer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this contract"
            )
    elif current_user.role == "buyer":
        result = await db.execute(
            select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
        )
        buyer = result.scalar_one_or_none()
        if not buyer or contract.buyer_id != buyer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this contract"
            )
    
    return ContractResponse(
        _id=str(contract.id),
        buyer_id=str(contract.buyer_id),
        buyer_name=contract.buyer_name,
        farmer_id=str(contract.farmer_id),
        farmer_name=contract.farmer_name,
        items=contract.items,
        total_amount=contract.total_amount,
        delivery_date=contract.delivery_date,
        delivery_address=contract.delivery_address,
        terms=contract.terms,
        notes=contract.notes,
        status=contract.status,
        contract_hash=contract.contract_hash,
        blockchain_tx_id=contract.blockchain_tx_id,
        farmer_signature=contract.farmer_signature,
        buyer_signature=contract.buyer_signature,
        created_at=contract.created_at,
        updated_at=contract.updated_at,
        signed_at=contract.signed_at,
        completed_at=contract.completed_at
    )


@router.post("/{contract_id}/sign", response_model=ContractResponse)
async def sign_contract(
    contract_id: str,
    sign_data: SignContractRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sign a contract (role-aware: farmer or buyer)"""
    result = await db.execute(
        select(Contract).where(Contract.id == UUID(contract_id))
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Check contract status
    if contract.status not in [ContractStatus.PENDING.value, ContractStatus.SIGNED_FARMER.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contract cannot be signed in status: {contract.status}"
        )
    
    # Handle signing based on role
    if current_user.role == "farmer":
        # Verify this is the farmer's contract
        result = await db.execute(
            select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
        )
        farmer = result.scalar_one_or_none()
        if not farmer or contract.farmer_id != farmer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to sign this contract"
            )
        
        # Check if already signed
        if contract.farmer_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Farmer has already signed this contract"
            )
        
        # Add farmer signature
        signature = {
            "signer_id": str(farmer.id),
            "signer_name": contract.farmer_name,
            "signer_role": "farmer",
            "signature": sign_data.signature,
            "public_key": sign_data.public_key,
            "signed_at": datetime.utcnow().isoformat()
        }
        contract.farmer_signature = signature
        
        # Update status based on buyer signature
        if contract.buyer_signature:
            contract.status = ContractStatus.ACTIVE.value
            contract.signed_at = datetime.utcnow()
        else:
            contract.status = ContractStatus.SIGNED_FARMER.value
    
    elif current_user.role == "buyer":
        # Verify this is the buyer's contract
        result = await db.execute(
            select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
        )
        buyer = result.scalar_one_or_none()
        if not buyer or contract.buyer_id != buyer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to sign this contract"
            )
        
        # Check if already signed
        if contract.buyer_signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Buyer has already signed this contract"
            )
        
        # Add buyer signature
        signature = {
            "signer_id": str(buyer.id),
            "signer_name": contract.buyer_name,
            "signer_role": "buyer",
            "signature": sign_data.signature,
            "public_key": sign_data.public_key,
            "signed_at": datetime.utcnow().isoformat()
        }
        contract.buyer_signature = signature
        
        # Update status based on farmer signature
        if contract.farmer_signature:
            contract.status = ContractStatus.ACTIVE.value
            contract.signed_at = datetime.utcnow()
        # Note: Buyer signing first keeps status as PENDING
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role for signing"
        )
    
    contract.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(contract)
    
    return ContractResponse(
        _id=str(contract.id),
        buyer_id=str(contract.buyer_id),
        buyer_name=contract.buyer_name,
        farmer_id=str(contract.farmer_id),
        farmer_name=contract.farmer_name,
        items=contract.items,
        total_amount=contract.total_amount,
        delivery_date=contract.delivery_date,
        delivery_address=contract.delivery_address,
        terms=contract.terms,
        notes=contract.notes,
        status=contract.status,
        contract_hash=contract.contract_hash,
        blockchain_tx_id=contract.blockchain_tx_id,
        farmer_signature=contract.farmer_signature,
        buyer_signature=contract.buyer_signature,
        created_at=contract.created_at,
        updated_at=contract.updated_at,
        signed_at=contract.signed_at,
        completed_at=contract.completed_at
    )


@router.post("/{contract_id}/reject")
async def reject_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reject a contract (farmer only)"""
    # Verify user is a farmer
    if current_user.role != "farmer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only farmers can reject contracts"
        )
    
    result = await db.execute(
        select(Contract).where(Contract.id == UUID(contract_id))
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Verify this is the farmer's contract
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
    )
    farmer = result.scalar_one_or_none()
    if not farmer or contract.farmer_id != farmer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to reject this contract"
        )
    
    # Check if contract can be rejected
    if contract.status not in [ContractStatus.PENDING.value, ContractStatus.SIGNED_FARMER.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Contract cannot be rejected in status: {contract.status}"
        )
    
    # Update contract status
    contract.status = ContractStatus.REJECTED.value
    contract.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Contract rejected successfully"}


@router.get("/{contract_id}/generate-keys", response_model=KeyPairResponse)
async def generate_signing_keys(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate RSA key pair for signing"""
    result = await db.execute(
        select(Contract).where(Contract.id == UUID(contract_id))
    )
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    # Verify user has access to this contract
    if current_user.role == "farmer":
        result = await db.execute(
            select(FarmerProfile).where(FarmerProfile.user_id == current_user.id)
        )
        farmer = result.scalar_one_or_none()
        if not farmer or contract.farmer_id != farmer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
    elif current_user.role == "buyer":
        result = await db.execute(
            select(BuyerProfile).where(BuyerProfile.user_id == current_user.id)
        )
        buyer = result.scalar_one_or_none()
        if not buyer or contract.buyer_id != buyer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
    
    # Generate keys
    private_key, public_key = generate_keys()
    
    return {
        "private_key": private_key,
        "public_key": public_key,
        "note": "Store the private key securely. It will not be shown again."
    }
