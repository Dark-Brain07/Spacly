import Link from "next/link";

export default function Home() {
  return (
    <main className="wrap">
      <section className="hero">
        <div>
          <div className="eyebrow">Intelligent Acceptance Protocol</div>
          <h1>Verify migrations with decentralized consensus.</h1>
          <p className="lead">
            SPACLY freezes bounded baseline evidence, anchors candidates through cryptographically sealed manifests and content hashes, and leverages GenLayer AI consensus for semantic boundary validation before production authorization.
          </p>
          <div className="buttonRow">
            <Link className="button hot" href="/migrations/new">
              Start a Migration
            </Link>
            <Link className="button ghost" href="/how">
              Explore Protocol
            </Link>
          </div>
        </div>
        <div className="heroCard">
          <div className="signal" />
          <div className="spaclyRail">
            <div>
              <span>BASELINE</span>
              <b>Frozen + Authenticated</b>
            </div>
            <i>→</i>
            <div>
              <span>CANDIDATE</span>
              <b>Manifest + Content SHA</b>
            </div>
            <i>→</i>
            <div>
              <span>VERDICT</span>
              <b>Evidence-Root Authorization</b>
            </div>
          </div>
        </div>
      </section>

      <section className="grid section">
        <div className="panel">
          <div className="eyebrow">Objective Probes</div>
          <h2>Status, headers and body identity checked.</h2>
          <p>Deterministic HTTP probes verify payload integrity before non-deterministic semantic evaluation.</p>
        </div>
        <div className="panel">
          <div className="eyebrow">Consensus Driven</div>
          <h2>Attempts are immutable and audited.</h2>
          <p>Semantic findings cannot be overwritten arbitrarily; challenge and assessment limits are deterministically enforced.</p>
        </div>
        <div className="panel">
          <div className="eyebrow">Evidence Root</div>
          <h2>Authorization commits proof hashes.</h2>
          <p>Final state binds manifest identity, baseline route digests, and validator agreement roots on-chain.</p>
        </div>
      </section>
    </main>
  );
}
