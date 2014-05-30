// This file is part of libigl, a simple c++ geometry processing library.
// 
// Copyright (C) 2013 Alec Jacobson <alecjacobson@gmail.com>
// 
// This Source Code Form is subject to the terms of the Mozilla Public License 
// v. 2.0. If a copy of the MPL was not distributed with this file, You can 
// obtain one at http://mozilla.org/MPL/2.0/.
#include "writeMESH.h"

#include "verbose.h"
#include "matrix_to_list.h"
#include <Eigen/Core>

#include <iostream>
#include <fstream>
#include <cstdio>

template <typename Scalar, typename Index>
IGL_INLINE bool igl::writeMESH(
  const std::string mesh_file_name,
  const std::vector<std::vector<Scalar > > & V,
  const std::vector<std::vector<Index > > & T,
  const std::vector<std::vector<Index > > & F)
{
  Eigen::MatrixXd mV;
  Eigen::MatrixXi mT,mF;
  bool is_rect;
  is_rect = list_to_matrix(V,mV);
  if(!is_rect)
  {
    return false;
  }
  is_rect = list_to_matrix(T,mT);
  if(!is_rect)
  {
    return false;
  }
  is_rect = list_to_matrix(F,mF);
  if(!is_rect)
  {
    return false;
  }
  return igl::writeMESH(mesh_file_name,mV,mT,mF);
}


template <typename DerivedV, typename DerivedT, typename DerivedF>
IGL_INLINE bool igl::writeMESH(
  const std::string str,
  const Eigen::PlainObjectBase<DerivedV> & V, 
  const Eigen::PlainObjectBase<DerivedT> & T,
  const Eigen::PlainObjectBase<DerivedF> & F)
{
  using namespace std;
  using namespace igl;
  using namespace Eigen;

  //// This is (surprisingly) slower than the C-ish code below
  //ofstream mesh_file;
  //mesh_file.open(str.c_str());
  //if(!mesh_file.is_open())
  //{
  //  cerr<<"IOError: "<<str<<" could not be opened..."<<endl;
  //  return false;
  //}
  //IOFormat format(FullPrecision,DontAlignCols," ","\n",""," 1","","");
  //mesh_file<<"MeshVersionFormatted 1\n";
  //mesh_file<<"Dimension 3\n";
  //mesh_file<<"Vertices\n";
  //mesh_file<<V.rows()<<"\n";
  //mesh_file<<V.format(format)<<"\n";
  //mesh_file<<"Triangles\n";
  //mesh_file<<F.rows()<<"\n";
  //mesh_file<<(F.array()+1).eval().format(format)<<"\n";
  //mesh_file<<"Tetrahedra\n";
  //mesh_file<<T.rows()<<"\n";
  //mesh_file<<(T.array()+1).eval().format(format)<<"\n";
  //mesh_file.close();

  FILE * mesh_file = fopen(str.c_str(),"w");
  if(NULL==mesh_file)
  {
    fprintf(stderr,"IOError: %s could not be opened...",str.c_str());
    return false;
  }
  // print header
  fprintf(mesh_file,"MeshVersionFormatted 1\n");
  fprintf(mesh_file,"Dimension 3\n");
  // print tet vertices
  fprintf(mesh_file,"Vertices\n");
  // print number of tet vertices
  int number_of_tet_vertices = V.rows();
  fprintf(mesh_file,"%d\n",number_of_tet_vertices);
  // loop over tet vertices
  for(int i = 0;i<number_of_tet_vertices;i++)
  {
    // print position of ith tet vertex
    fprintf(mesh_file,"%lg %lg %lg 1\n",
      (double)V(i,0),
      (double)V(i,1),
      (double)V(i,2));
  }
  verbose("WARNING: save_mesh() assumes that vertices have"
      " same indices in surface as volume...\n");
  // print faces
  fprintf(mesh_file,"Triangles\n");
  // print number of triangles
  int number_of_triangles = F.rows();
  fprintf(mesh_file,"%d\n",number_of_triangles);
  // loop over faces
  for(int i = 0;i<number_of_triangles;i++)
  {
    // loop over vertices in face
    fprintf(mesh_file,"%d %d %d 1\n", 
      (int)F(i,0)+1, 
      (int)F(i,1)+1, 
      (int)F(i,2)+1);
  }
  // print tetrahedra
  fprintf(mesh_file,"Tetrahedra\n");
  int number_of_tetrahedra = T.rows();
  // print number of tetrahedra
  fprintf(mesh_file,"%d\n",number_of_tetrahedra);
  // loop over tetrahedra
  for(int i = 0; i < number_of_tetrahedra;i++)
  {
    // mesh standard uses 1-based indexing
    fprintf(mesh_file, "%d %d %d %d 1\n",
      (int)T(i,0)+1,
      (int)T(i,1)+1,
      (int)T(i,2)+1,
      (int)T(i,3)+1);
  }
  fclose(mesh_file);
  return true;
}

#ifndef IGL_HEADER_ONLY
// Explicit template specialization
//template bool igl::writeMESH<Eigen::Matrix<double, -1, -1, 0, -1, -1>, Eigen::Matrix<int, -1, -1, 0, -1, -1>, Eigen::Matrix<int, -1, -1, 0, -1, -1> >(std::basic_string<char, std::char_traits<char>, std::allocator<char> >, Eigen::MatrixBase<Eigen::Matrix<double, -1, -1, 0, -1, -1> > const&, Eigen::MatrixBase<Eigen::Matrix<int, -1, -1, 0, -1, -1> > const&, Eigen::MatrixBase<Eigen::Matrix<int, -1, -1, 0, -1, -1> > const&);
template bool igl::writeMESH<Eigen::Matrix<double, -1, -1, 0, -1, -1>, Eigen::Matrix<int, -1, -1, 0, -1, -1>, Eigen::Matrix<int, -1, -1, 0, -1, -1> >(std::basic_string<char, std::char_traits<char>, std::allocator<char> >, Eigen::PlainObjectBase<Eigen::Matrix<double, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<int, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<int, -1, -1, 0, -1, -1> > const&);
#endif
