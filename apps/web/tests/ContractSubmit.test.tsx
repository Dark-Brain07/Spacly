import React from "react";
import {afterEach,beforeEach,describe,expect,it,vi} from "vitest";
import {fireEvent,render,screen,waitFor,cleanup} from "@testing-library/react";
import {ExecutionResult,TransactionStatus} from "genlayer-js/types";

const {getTransaction,writeSpacly,readSpacly,refresh}=vi.hoisted(()=>({
  getTransaction:vi.fn(),writeSpacly:vi.fn(),readSpacly:vi.fn(),refresh:vi.fn(),
}));
vi.mock("genlayer-js",()=>({createClient:()=>({getTransaction})}));
vi.mock("genlayer-js/chains",()=>({studionet:{id:61999}}));
vi.mock("next/navigation",()=>({useRouter:()=>({refresh})}));
vi.mock("@/lib/contract",()=>({readSpacly,writeSpacly}));
vi.mock("@/lib/config",()=>({isConfigured:()=>true,NETWORK:{explorer:"https://explorer.studio.genlayer.com"}}));
vi.mock("../components/WalletSession",()=>({useWallet:()=>({provider:{request:vi.fn()},account:"0x1111111111111111111111111111111111111111",networkOk:true})}));

import {useContractSubmit,TxFeedback} from "../components/ContractSubmit";

const HASH=("0x"+"b".repeat(64)) as `0x${string}`;

function Harness(){
  const tx=useContractSubmit();
  return <><button type="button" onClick={()=>void tx.submit("authorize",[3],3).catch(()=>undefined)}>Submit</button>
    <output data-testid="phase">{tx.phase??"none"}</output>
    <TxFeedback phase={tx.phase} message={tx.message} confirmed={tx.confirmed} pending={tx.pending} onRecover={tx.recover} busy={tx.busy}/>
  </>;
}

describe("contract submission recovery",()=>{
  beforeEach(()=>{sessionStorage.clear();getTransaction.mockReset();writeSpacly.mockReset();readSpacly.mockReset();refresh.mockReset();});
  afterEach(cleanup);

  it("labels a rejected wallet signature and stores no transaction",async()=>{
    writeSpacly.mockRejectedValueOnce(Object.assign(new Error("User rejected request"),{code:4001}));
    render(<Harness/>);
    fireEvent.click(screen.getByRole("button",{name:"Submit"}));
    await waitFor(()=>expect(screen.getByTestId("phase").textContent).toBe("signature_rejected"));
    expect(screen.getByText("Wallet signature was rejected; no transaction was submitted.")).toBeTruthy();
    expect(screen.queryByRole("button",{name:"Resume status tracking"})).toBeNull();
    expect(sessionStorage.length).toBe(0);
  });

  it("renders structured provider failures instead of object Object",async()=>{
    writeSpacly.mockRejectedValueOnce({code:-32000,message:"Studionet write failed",data:{details:"RPC rejected transaction"}});
    render(<Harness/>);
    fireEvent.click(screen.getByRole("button",{name:"Submit"}));
    await waitFor(()=>expect(screen.getByTestId("phase").textContent).toBe("submission_error"));
    expect(screen.getByText(/Studionet write failed/)).toBeTruthy();
    expect(screen.queryByText("[object Object]")).toBeNull();
    expect(sessionStorage.length).toBe(0);
  });

  it("restores an RPC-interrupted hash after refresh, resumes polling, and re-reads final state",async()=>{
    writeSpacly.mockResolvedValueOnce(HASH);
    getTransaction.mockRejectedValueOnce(new Error("RPC offline"));
    getTransaction.mockResolvedValueOnce({statusName:TransactionStatus.FINALIZED,txExecutionResultName:ExecutionResult.FINISHED_WITH_RETURN});
    readSpacly.mockResolvedValueOnce({id:3,state:"AUTHORIZED"});

    const first=render(<Harness/>);
    fireEvent.click(screen.getByRole("button",{name:"Submit"}));
    await waitFor(()=>expect(screen.getByTestId("phase").textContent).toBe("rpc_error"));
    expect(sessionStorage.getItem("spacly.pendingTransaction.v1")).toContain(HASH);
    expect(screen.getByRole("button",{name:"Resume status tracking"})).toBeTruthy();

    first.unmount();
    render(<Harness/>);
    await waitFor(()=>expect(screen.getByTestId("phase").textContent).toBe("submitted"));
    fireEvent.click(screen.getByRole("button",{name:"Resume status tracking"}));

    await waitFor(()=>expect(screen.getByTestId("phase").textContent).toBe("execution_success"));
    expect(readSpacly).toHaveBeenCalledWith("get_migration",[3]);
    expect(sessionStorage.getItem("spacly.pendingTransaction.v1")).toBeNull();
    expect(refresh).toHaveBeenCalledOnce();
  });

  it("treats a production-shaped Studio FINALIZED/SUCCESS transaction as successful without txExecutionResultName",async()=>{
    writeSpacly.mockResolvedValueOnce(HASH);
    getTransaction.mockResolvedValueOnce({
      statusName:TransactionStatus.FINALIZED,
      consensus_data:{leader_receipt:[{execution_result:"SUCCESS"}]},
    });
    readSpacly.mockResolvedValueOnce({id:3,state:"CANDIDATE"});

    render(<Harness/>);
    fireEvent.click(screen.getByRole("button",{name:"Submit"}));

    await waitFor(()=>expect(screen.getByTestId("phase").textContent).toBe("execution_success"));
    expect(readSpacly).toHaveBeenCalledWith("get_migration",[3]);
    expect(screen.getByText("Finalized successfully; contract state re-read from LATEST_FINAL.")).toBeTruthy();
    expect(screen.queryByText("EXECUTION FAILURE")).toBeNull();
    expect(screen.queryByText(/UNKNOWN/)).toBeNull();
    expect(sessionStorage.getItem("spacly.pendingTransaction.v1")).toBeNull();
    expect(refresh).toHaveBeenCalledOnce();
  });

  it("rereads contract state after a Studio finalized execution ERROR",async()=>{
    writeSpacly.mockResolvedValueOnce(HASH);
    getTransaction.mockResolvedValueOnce({
      statusName:TransactionStatus.FINALIZED,
      consensus_data:{leader_receipt:[{execution_result:"ERROR"}]},
    });
    readSpacly.mockResolvedValueOnce({id:3,state:"CANDIDATE"});
    render(<Harness/>);
    fireEvent.click(screen.getByRole("button",{name:"Submit"}));
    await waitFor(()=>expect(screen.getByTestId("phase").textContent).toBe("execution_failure"));
    expect(readSpacly).toHaveBeenCalledWith("get_migration",[3]);
    expect(screen.getByText(/"state": "CANDIDATE"/)).toBeTruthy();
    expect(sessionStorage.getItem("spacly.pendingTransaction.v1")).toBeNull();
    expect(refresh).toHaveBeenCalledOnce();
  });

  it("keeps normalized FINISHED_WITH_ERROR failure handling",async()=>{
    writeSpacly.mockResolvedValueOnce(HASH);
    getTransaction.mockResolvedValueOnce({statusName:TransactionStatus.FINALIZED,txExecutionResultName:ExecutionResult.FINISHED_WITH_ERROR});
    readSpacly.mockResolvedValueOnce({id:3,state:"CANDIDATE"});
    render(<Harness/>);
    fireEvent.click(screen.getByRole("button",{name:"Submit"}));
    await waitFor(()=>expect(screen.getByTestId("phase").textContent).toBe("execution_failure"));
    expect(readSpacly).toHaveBeenCalledWith("get_migration",[3]);
  });

  it("labels genuinely unavailable execution evidence accurately and still rereads finalized state",async()=>{
    writeSpacly.mockResolvedValueOnce(HASH);
    getTransaction.mockResolvedValueOnce({statusName:TransactionStatus.FINALIZED});
    readSpacly.mockResolvedValueOnce({id:3,state:"CANDIDATE"});
    render(<Harness/>);
    fireEvent.click(screen.getByRole("button",{name:"Submit"}));
    await waitFor(()=>expect(screen.getByTestId("phase").textContent).toBe("execution_unavailable"));
    expect(screen.getByText("GenLayer transaction finalized, but its execution result is unavailable from both normalized SDK and Studio leader receipt data.")).toBeTruthy();
    expect(screen.queryByText("EXECUTION FAILURE")).toBeNull();
    expect(screen.queryByText(/UNKNOWN/)).toBeNull();
    expect(readSpacly).toHaveBeenCalledWith("get_migration",[3]);
    expect(screen.getByText(/"state": "CANDIDATE"/)).toBeTruthy();
    expect(refresh).toHaveBeenCalledOnce();
  });
});
