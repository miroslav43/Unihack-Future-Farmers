export type ContractStatus = 
  | 'pending' 
  | 'signed_farmer' 
  | 'active' 
  | 'completed' 
  | 'cancelled' 
  | 'rejected';

export interface Signature {
  signer_id: string;
  signer_name: string;
  signer_role: string;
  signature: string;
  signed_at: string;
  public_key: string;
}

export interface ContractItem {
  product_id: string;
  product_name: string;
  quantity: number;
  unit: string;
  price_per_unit: number;
  total_price: number;
}

export interface Contract {
  _id: string;
  buyer_id: string;
  buyer_name: string;
  farmer_id: string;
  farmer_name: string;
  items: ContractItem[];
  total_amount: number;
  delivery_date?: string;
  delivery_address?: string;
  terms?: string;
  notes?: string;
  status: ContractStatus;
  contract_hash: string;
  blockchain_tx_id?: string;
  farmer_signature?: Signature;
  buyer_signature?: Signature;
  created_at: string;
  updated_at: string;
  signed_at?: string;
  completed_at?: string;
}

export interface CreateContractRequest {
  buyer_id: string;
  buyer_name: string;
  farmer_id: string;
  farmer_name: string;
  items: ContractItem[];
  total_amount: number;
  delivery_date?: string;
  delivery_address?: string;
  terms?: string;
  notes?: string;
}

export interface SignContractRequest {
  signature: string;
  public_key: string;
}

export interface KeyPair {
  private_key: string;
  public_key: string;
  note: string;
}
