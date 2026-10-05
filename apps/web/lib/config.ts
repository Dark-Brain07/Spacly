export const NETWORK = {
  name: "studionet",
  chainId: 61999,
  rpc: "https://studio.genlayer.com/api",
  explorer: "https://explorer-studio.genlayer.com",
} as const;

export const CONTRACT_ADDRESS =
  process.env.NEXT_PUBLIC_SPACLY_CONTRACT_ADDRESS?.trim() ||
  process.env.NEXT_PUBLIC_CUTOVER_CONTRACT_ADDRESS?.trim() ||
  "0x860De7Dc72128C1F2A7EF9d415761641B05C25Bb";

export const isConfigured = () => /^0x[a-fA-F0-9]{40}$/.test(CONTRACT_ADDRESS);
