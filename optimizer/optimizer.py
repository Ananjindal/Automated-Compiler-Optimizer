from optimizer.constant_folding import constant_folding
from optimizer.constant_propagation import constant_propagation
from optimizer.algebraic_simplification import (
    algebraic_simplification
)
from optimizer.cse import (
    common_subexpression_elimination
)
from optimizer.dead_code_elimination import (
    dead_code_elimination
)
from optimizer.strength_reduction import (
    strength_reduction
)


class Optimizer:

    def __init__(self, max_passes=20):

        self.max_passes = max_passes

        self.optimization_log = []

        self.pass_history = []

    # ==========================================
    # OPTIMIZE
    # ==========================================

    def optimize(self, tac):

        current_tac = tac.copy()

        self.optimization_log = []
        self.pass_history = []

        for pass_number in range(
            1,
            self.max_passes + 1
        ):

            previous_tac = current_tac.copy()

            # ==================================
            # 1. CONSTANT FOLDING
            # ==================================

            current_tac, changes = (
                constant_folding(current_tac)
            )

            self.record_changes(
                pass_number,
                "Constant Folding",
                changes
            )

            # ==================================
            # 2. CONSTANT PROPAGATION
            # ==================================

            current_tac, changes = (
                constant_propagation(current_tac)
            )

            self.record_changes(
                pass_number,
                "Constant Propagation",
                changes
            )

            # ==================================
            # 3. ALGEBRAIC SIMPLIFICATION
            # ==================================

            current_tac, changes = (
                algebraic_simplification(
                    current_tac
                )
            )

            self.record_changes(
                pass_number,
                "Algebraic Simplification",
                changes
            )

            # ==================================
            # 4. COMMON SUBEXPRESSION
            # ==================================

            current_tac, changes = (
                common_subexpression_elimination(
                    current_tac
                )
            )

            self.record_changes(
                pass_number,
                "Common Subexpression Elimination",
                changes
            )

            # ==================================
            # 5. DEAD CODE ELIMINATION
            # ==================================

            current_tac, changes = (
                dead_code_elimination(
                    current_tac
                )
            )

            self.record_changes(
                pass_number,
                "Dead Code Elimination",
                changes
            )

            # ==================================
            # 6. STRENGTH REDUCTION
            # ==================================

            current_tac, changes = (
                strength_reduction(
                    current_tac
                )
            )

            self.record_changes(
                pass_number,
                "Strength Reduction",
                changes
            )

            # ==================================
            # CHECK WHETHER TAC CHANGED
            # ==================================

            changed = (
                current_tac != previous_tac
            )

            self.pass_history.append({
                "pass": pass_number,
                "instruction_count": len(
                    current_tac
                ),
                "changed": changed
            })

            # ==================================
            # FIXED POINT
            # ==================================

            if not changed:

                break

        return current_tac

    # ==========================================
    # RECORD CHANGES
    # ==========================================

    def record_changes(
        self,
        pass_number,
        optimizer_name,
        changes
    ):

        for change in changes:

            self.optimization_log.append({
                "pass": pass_number,
                "optimizer": optimizer_name,
                "change": change
            })

    # ==========================================
    # GET LOG
    # ==========================================

    def get_optimization_log(self):

        return self.optimization_log

    # ==========================================
    # GET PASS HISTORY
    # ==========================================

    def get_pass_history(self):

        return self.pass_history


# ==========================================
# PUBLIC FUNCTION
# ==========================================

def optimize_tac(tac):

    optimizer = Optimizer()

    optimized_tac = optimizer.optimize(tac)

    return (
        optimized_tac,
        optimizer.get_optimization_log(),
        optimizer.get_pass_history()
    )