from bezier_utility import *
from weight_inverse_distance import *

class Bundle( object ):
	def __init__( self, Ws, control_points, constraints, weight ):
		self.Ws = Ws
		self.control_points = control_points
		self.constraints = asarray( constraints )
		self.weight = weight

# class Constraint( object ):
#     def __init__( self, smoothness, position_is_fixed ):
#         '''
#         The parameter 'smoothness' must be one of 'C0', 'C1', 'G1', or 'A'.
#         The parameter 'position_is_fixed' is a boolean.
#         '''
#         self.smoothness = smoothness
#         self.position_is_fixed = position_is_fixed

class BezierConstraintSolver( object ):
	def __init__( self, W_matrices, control_points, constraints, transforms, is_closed ):
    	## compute the weight of each segment according to its length
		num = len(control_points)
		weights = asarray([length_of_cubic_bezier_curve(P) for P in control_points])
		weights = weights/sum(weights)
		self.build_system( W_matrices, control_points, constraints, transforms, is_closed, weights )

	def build_system( self, W_matrices, control_points, constraints, transforms, is_closed, weights ):
        
        ### 1 Bundle all data for each bezier curve together
        ### 2 Allocate space for the system matrix
        ### 3 Gather the pieces of the system for each curve
        ### 4 Insert them into the system matrix and right-hand-side
        ### 5 Gather the lagrange equations between adjacent curves
        ### 6 Insert them into the system matrix and right-hand-side

		### 1
		self.bundles = [ Bundle( W_matrices[i], control_points[i], [constraints[i], 
						constraints[(i+1)%len(control_points)]], weights[i] ) 
						for i in xrange(len( control_points )) ]
						
		self.dofs_per_bundle = [ self.compute_dofs_per_curve( bundle ) 
						for bundle in self.bundles ]
						
		self.lambdas_per_joint = [ self.constraint_number_per_joint( constraint ) 
						for constraint in constraints]
						
		### 2
		self.total_dofs = sum( self.dofs_per_bundle ) 
		self.system_size = self.total_dofs + sum( self.lambdas_per_joint )
		self.system = zeros( ( self.system_size, self.system_size ) )
		self.rhs = zeros( self.system_size )

		## For convenience, set local variables from instance variables.
		## WARNING: If you re-assign one of these, the instance variable will not be updated!
		bundles = self.bundles
		dofs_per_bundle = self.dofs_per_bundle
		lambdas_per_joint = self.lambdas_per_joint
		total_dofs = self.total_dofs
		system_size = self.system_size
		system = self.system
		rhs = self.rhs


		### 3
		dof_offset = 0
		for i in range(len( bundles )):
			bundle = bundles[i]
			dofs = sum(dofs_per_bundle[i])
	
			small_system = self.system_for_curve( bundle )
			small_rhs = self.rhs_for_curve(bundle, transforms)
			### 4
			system[ dof_offset : dof_offset + dofs, dof_offset : dof_offset + dofs ] = small_system
			rhs[ dof_offset : dof_offset + dofs ] = small_rhs
	
			dof_offset += dofs

		assert dof_offset == total_dofs
        

		### 5
		dof_offset = 0
		constraint_equation_offset = total_dofs
		for i in range( len( bundles ) - 1 ):
			dofs = sum(dofs_per_bundle[i])
			dofs_next = sum(dofs_per_bundle[i+1])
			constraint_eqs = lambdas_per_joint[i+1]
	
			small_lagrange_system, small_lagrange_rhs = self.lagrange_equations_for_curve_constraints( bundles[i], bundles[i+1] )
	
			### 4
			system[ constraint_equation_offset : constraint_equation_offset + constraint_eqs, 
					dof_offset : dof_offset + dofs + dofs_next ] = small_lagrange_system
			rhs[ constraint_equation_offset : constraint_equation_offset + constraint_eqs ] = small_lagrange_rhs
	
			dof_offset += dofs
			constraint_equation_offset += constraint_eqs

		## Handle the connection between the last and first bezier curves if it is a closed curve.
		if is_closed:
			dofs = sum(dofs_per_bundle[-1])
			dofs_next = sum(dofs_per_bundle[0])
			constraint_eqs = lambdas_per_joint[0]
	
			small_lagrange_system, small_lagrange_rhs = self.lagrange_equations_for_curve_constraints( bundles[-1], bundles[0] )
	
			### 4
			system[ constraint_equation_offset : constraint_equation_offset + constraint_eqs, dof_offset : dof_offset + dofs  ] = small_lagrange_system[ :, :dofs ]
			system[ constraint_equation_offset : constraint_equation_offset + constraint_eqs,
					: dofs_next ] = small_lagrange_system[ :, dofs: ]
			rhs[ constraint_equation_offset : constraint_equation_offset + constraint_eqs ] = small_lagrange_rhs

		## Set the upper-right portion of the system matrix, too
		system[ : total_dofs, total_dofs : ] = system.T[ : total_dofs, total_dofs : ]


	def update_rhs_for_handles( self, transforms ):
		dof_offset = 0
		for i in range(len( bundles )):
			bundle = self.bundles[i]
			dofs = self.dofs_per_bundle[i]
	
			small_rhs = self.rhs_for_curve( bundle, transforms )
			### 4
			self.rhs[ dof_offset : dof_offset + dofs ] = small_rhs
	
			dof_offset += dofs

		assert dof_offset == self.total_dofs

	### For subclasses to implement:
	def update_system_with_result_of_previous_iteration( self, previous_solution ):
		raise NotImplementedError( "This is an abstract base class. Only call this on a subclass." )

	def solve( self ):
		x = linalg.solve( self.system, self.rhs )
	
		### Return a nicely formatted chain of bezier curves,
		### even if some of the variables were substituted in the actual system matrix.
		raise NotImplementedError( "This is an abstract base class. Only call this on a subclass." )

	def lagrange_equations_for_curve_constraints( self, bundle0, bundle1):
		raise NotImplementedError( "This is an abstract base class. Only call this on a subclass." )
	def system_for_curve( self, bundle ):
		raise NotImplementedError( "This is an abstract base class. Only call this on a subclass." )
	def compute_dofs_per_curve( self, bundle ):
		raise NotImplementedError( "This is an abstract base class. Only call this on a subclass." )
	def constraint_number_per_joint( self, constraint ):
		raise NotImplementedError( "This is an abstract base class. Only call this on a subclass." )
	def rhs_for_curve( self, bundle, transforms ):
		raise NotImplementedError( "This is an abstract base class. Only call this on a subclass." )



