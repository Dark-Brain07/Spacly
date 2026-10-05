export default function Page() {
  const workflow = `- name: Verify finalized SPACLY authorization
  uses: spacly/packages/gate@main
  with:
    contract-address: \${{ vars.SPACLY_CONTRACT_ADDRESS }}
    migration-id: \${{ vars.SPACLY_MIGRATION_ID }}
    expected-candidate-ref: \${{ github.sha }}
    chain-id: '61999'`;

  return (
    <main className="wrap section">
      <div className="eyebrow">Release Infrastructure</div>
      <h1>Repository-consumable read-only deployment gate.</h1>
      <p className="lead">
        The bundled GitHub Action reads finalized on-chain state from the SPACLY intelligent contract. It validates AUTHORIZED status, current generation, exact release ref, matching manifest digest, and the 32-byte cryptographic evidence root.
      </p>
      <pre>{workflow}</pre>
      <p className="notice">
        This gate requires zero gas or private keys. It performs read-only consensus verification directly against GenLayer StudioNet.
      </p>
    </main>
  );
}
