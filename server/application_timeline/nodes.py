"""The six fixed loan-application timeline nodes (the backbone of Function 3).

The order and codes are a closed set: applications always have exactly these six
nodes, the admin can only advance the *current* node (no skipping), and the SME
sees the same fixed sequence with bilingual labels.
"""
from __future__ import annotations

# (node_code, sort_order, label_zh, label_en)
NODES: list[tuple[str, int, str, str]] = [
    ("submitted", 1, "已提交", "Submitted"),
    ("material_review", 2, "材料审核", "Material Review"),
    ("credit_assessment", 3, "信用评估", "Credit Assessment"),
    ("approval_result", 4, "审批结果", "Approval Result"),
    ("signing", 5, "签约", "Signing"),
    ("disbursement", 6, "放款", "Disbursement"),
]

NODE_CODES: list[str] = [code for code, _, _, _ in NODES]
NODE_LABELS: dict[str, dict[str, str]] = {
    code: {"zh": zh, "en": en} for code, _, zh, en in NODES
}
SORT_ORDER: dict[str, int] = {code: order for code, order, _, _ in NODES}

# New application: submitted is already done, material review is active, rest wait.
INITIAL_NODE_STATES: dict[str, str] = {
    "submitted": "completed",
    "material_review": "in_progress",
}
INITIAL_CURRENT_NODE = "material_review"
DEFAULT_NODE_STATE = "pending"

NODE_STATES = frozenset(
    {"pending", "in_progress", "completed", "rejected", "supplement_required"}
)
# States the admin may explicitly set on the current node.
ADMIN_SETTABLE_STATES = frozenset(
    {"in_progress", "completed", "rejected", "supplement_required"}
)
# Setting one of these on the current node requires bilingual customer notes.
STATES_REQUIRING_CUSTOMER_NOTE = frozenset({"rejected", "supplement_required"})


def initial_state_for(node_code: str) -> str:
    return INITIAL_NODE_STATES.get(node_code, DEFAULT_NODE_STATE)


def next_node_code(node_code: str) -> str | None:
    """The code of the node after ``node_code``, or None if it is the last node."""
    order = SORT_ORDER.get(node_code)
    if order is None:
        return None
    for code, sort_order, _, _ in NODES:
        if sort_order == order + 1:
            return code
    return None
