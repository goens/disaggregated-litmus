;; The background theory is linear integer arithmetic
(set-logic LIA)

;; Name and signature of the function to be synthesized
(synth-fun assertion ((x Int) (y Int)) Bool

    ;; Declare the non-terminals that would be used in the grammar
    ((Cond Bool) (Term Int))

    ;; Define the grammar for allowed implementations of max2
    (
     (Cond Bool ((and Cond Cond) (not Cond)
              (= Term Term) (<= Term Term) )) ;; (>= Term Term) does this make a difference?
     (Term Int (x y 0 1 2
             (ite Cond Term Term)))
     )
)

(declare-var x Int)
(declare-var y Int)

;; Define the semantic constraints on the function
;; Correct for any ordering of the transactions
;; Incorrect for some ordering of the statements inside the transactions
;;
;; Transaction 1
;; x = 1
;; y = 1
;;
;; Transaction 2
;; x = 2
;; y = 2
;;
;; T1; T2
(constraint (assertion 2 2))
;; T2; T1
(constraint (assertion 1 1))
;; T1.1; T2.1; T1.2; T2.2
(constraint (or
             ;; T1.1; T2.1; T1.2; T2.2
             (not (assertion 2 2))
             ;; T2.1; T1.1; T1.2; T2.2
             (not (assertion 1 2))
             ;; T1.1; T2.1; T2.2; T1.2
             (not (assertion 2 1))
             ;; T2.1; T1.1; T2.2; T1.2
             (not (assertion 1 1))
             ;; ...
             (not (assertion 0 0))
             ;; ...
             (not (assertion 0 1))
             ;; ...
             (not (assertion 0 2))
             ;; ...
             (not (assertion 1 0))
             ;; ...
             (not (assertion 1 1))
             ;; ...
             (not (assertion 1 2))
             ;; ...
             (not (assertion 2 0))
             ;; ...
             (not (assertion 2 1))
             ;; ...
             (not (assertion 2 2))
             ))

(check-synth)
