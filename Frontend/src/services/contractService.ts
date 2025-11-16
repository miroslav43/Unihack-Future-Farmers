import { Contract, CreateContractRequest, KeyPair, SignContractRequest } from '@/types/contract';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const contractService = {
  /**
   * Create a new contract (Buyer only)
   */
  async createContract(contractData: CreateContractRequest): Promise<Contract> {
    const response = await axios.post(`${API_BASE_URL}/contracts/`, contractData);
    return response.data;
  },

  /**
   * Get all contracts for current user
   */
  async getContracts(statusFilter?: string): Promise<Contract[]> {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const response = await axios.get(`${API_BASE_URL}/contracts/`, { params });
    return response.data;
  },

  /**
   * Get contract by ID
   */
  async getContract(contractId: string): Promise<Contract> {
    const response = await axios.get(`${API_BASE_URL}/contracts/${contractId}`);
    return response.data;
  },

  /**
   * Sign a contract
   */
  async signContract(contractId: string, signData: SignContractRequest): Promise<Contract> {
    const response = await axios.post(
      `${API_BASE_URL}/contracts/${contractId}/sign`,
      signData
    );
    return response.data;
  },

  /**
   * Reject a contract (Farmer only)
   */
  async rejectContract(contractId: string): Promise<{ message: string }> {
    const response = await axios.post(`${API_BASE_URL}/contracts/${contractId}/reject`);
    return response.data;
  },

  /**
   * Generate key pair for signing
   */
  async generateKeys(contractId: string): Promise<KeyPair> {
    const response = await axios.get(`${API_BASE_URL}/contracts/${contractId}/generate-keys`);
    return response.data;
  },
};
