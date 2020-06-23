/*
  * Copyright (c) 2015 Cryptonomex, Inc., and contributors.
  *
  * The MIT License
  *
  * Permission is hereby granted, free of charge, to any person obtaining a copy
  * of this software and associated documentation files (the "Software"), to deal
  * in the Software without restriction, including without limitation the rights
  * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  * copies of the Software, and to permit persons to whom the Software is
  * furnished to do so, subject to the following conditions:
  *
  * The above copyright notice and this permission notice shall be included in
  * all copies or substantial portions of the Software.
  *
  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  * THE SOFTWARE.
  */

#include <boost/test/unit_test.hpp>

#include <hive/chain/hive_fwd.hpp>

#include <hive/chain/database.hpp>
#include <hive/protocol/protocol.hpp>

#include <hive/protocol/hive_operations.hpp>
#include <hive/protocol/types.hpp>
#include <hive/chain/account_object.hpp>
#include <hive/chain/block_summary_object.hpp>
#include <hive/chain/hive_objects.hpp>
#include <hive/chain/sps_objects.hpp>
#include <hive/chain/transaction_object.hpp>
#include <hive/chain/util/tiny_asset.hpp>

#include <hive/chain/util/reward.hpp>

#include <fc/crypto/digest.hpp>
#include <fc/crypto/hex.hpp>
#include "../db_fixture/database_fixture.hpp"
#include "ios_utils.hpp"

#include <algorithm>
#include <random>
#include <ostream>

using namespace hive;
using namespace hive::chain;
using namespace hive::protocol;

BOOST_FIXTURE_TEST_SUITE( basic_tests, clean_database_fixture )

BOOST_AUTO_TEST_CASE( parse_size_test )
{
  BOOST_CHECK_THROW( fc::parse_size( "" ), fc::parse_error_exception );
  BOOST_CHECK_THROW( fc::parse_size( "k" ), fc::parse_error_exception );

  BOOST_CHECK_EQUAL( fc::parse_size( "0" ), 0 );
  BOOST_CHECK_EQUAL( fc::parse_size( "1" ), 1 );
  BOOST_CHECK_EQUAL( fc::parse_size( "2" ), 2 );
  BOOST_CHECK_EQUAL( fc::parse_size( "3" ), 3 );
  BOOST_CHECK_EQUAL( fc::parse_size( "4" ), 4 );

  BOOST_CHECK_EQUAL( fc::parse_size( "9" ),   9 );
  BOOST_CHECK_EQUAL( fc::parse_size( "10" ), 10 );
  BOOST_CHECK_EQUAL( fc::parse_size( "11" ), 11 );
  BOOST_CHECK_EQUAL( fc::parse_size( "12" ), 12 );

  BOOST_CHECK_EQUAL( fc::parse_size( "314159265"), 314159265 );
  BOOST_CHECK_EQUAL( fc::parse_size( "1k" ), 1024 );
  BOOST_CHECK_THROW( fc::parse_size( "1a" ), fc::parse_error_exception );
  BOOST_CHECK_EQUAL( fc::parse_size( "1kb" ), 1000 );
  BOOST_CHECK_EQUAL( fc::parse_size( "1MiB" ), 1048576 );
  BOOST_CHECK_EQUAL( fc::parse_size( "32G" ), 34359738368 );
}

/**
  * Verify that names are RFC-1035 compliant https://tools.ietf.org/html/rfc1035
  * https://github.com/cryptonomex/graphene/issues/15
  */
BOOST_AUTO_TEST_CASE( valid_name_test )
{
  BOOST_CHECK( !is_valid_account_name( "a" ) );
  BOOST_CHECK( !is_valid_account_name( "A" ) );
  BOOST_CHECK( !is_valid_account_name( "0" ) );
  BOOST_CHECK( !is_valid_account_name( "." ) );
  BOOST_CHECK( !is_valid_account_name( "-" ) );

  BOOST_CHECK( !is_valid_account_name( "aa" ) );
  BOOST_CHECK( !is_valid_account_name( "aA" ) );
  BOOST_CHECK( !is_valid_account_name( "a0" ) );
  BOOST_CHECK( !is_valid_account_name( "a." ) );
  BOOST_CHECK( !is_valid_account_name( "a-" ) );

  BOOST_CHECK( is_valid_account_name( "aaa" ) );
  BOOST_CHECK( !is_valid_account_name( "aAa" ) );
  BOOST_CHECK( is_valid_account_name( "a0a" ) );
  BOOST_CHECK( !is_valid_account_name( "a.a" ) );
  BOOST_CHECK( is_valid_account_name( "a-a" ) );

  BOOST_CHECK( is_valid_account_name( "aa0" ) );
  BOOST_CHECK( !is_valid_account_name( "aA0" ) );
  BOOST_CHECK( is_valid_account_name( "a00" ) );
  BOOST_CHECK( !is_valid_account_name( "a.0" ) );
  BOOST_CHECK( is_valid_account_name( "a-0" ) );

  BOOST_CHECK(  is_valid_account_name( "aaa-bbb-ccc" ) );
  BOOST_CHECK(  is_valid_account_name( "aaa-bbb.ccc" ) );

  BOOST_CHECK( !is_valid_account_name( "aaa,bbb-ccc" ) );
  BOOST_CHECK( !is_valid_account_name( "aaa_bbb-ccc" ) );
  BOOST_CHECK( !is_valid_account_name( "aaa-BBB-ccc" ) );

  BOOST_CHECK( !is_valid_account_name( "1aaa-bbb" ) );
  BOOST_CHECK( !is_valid_account_name( "-aaa-bbb-ccc" ) );
  BOOST_CHECK( !is_valid_account_name( ".aaa-bbb-ccc" ) );
  BOOST_CHECK( !is_valid_account_name( "/aaa-bbb-ccc" ) );

  BOOST_CHECK( !is_valid_account_name( "aaa-bbb-ccc-" ) );
  BOOST_CHECK( !is_valid_account_name( "aaa-bbb-ccc." ) );
  BOOST_CHECK( !is_valid_account_name( "aaa-bbb-ccc.." ) );
  BOOST_CHECK( !is_valid_account_name( "aaa-bbb-ccc/" ) );

  BOOST_CHECK( !is_valid_account_name( "aaa..bbb-ccc" ) );
  BOOST_CHECK( is_valid_account_name( "aaa.bbb-ccc" ) );
  BOOST_CHECK( is_valid_account_name( "aaa.bbb.ccc" ) );

  BOOST_CHECK(  is_valid_account_name( "aaa--bbb--ccc" ) );
  BOOST_CHECK( !is_valid_account_name( "xn--san-p8a.de" ) );
  BOOST_CHECK(  is_valid_account_name( "xn--san-p8a.dex" ) );
  BOOST_CHECK( !is_valid_account_name( "xn-san-p8a.de" ) );
  BOOST_CHECK(  is_valid_account_name( "xn-san-p8a.dex" ) );

  BOOST_CHECK(  is_valid_account_name( "this-label-has" ) );
  BOOST_CHECK( !is_valid_account_name( "this-label-has-more-than-63-char.act.ers-64-to-be-really-precise" ) );
  BOOST_CHECK( !is_valid_account_name( "none.of.these.labels.has.more.than-63.chars--but.still.not.valid" ) );
}

BOOST_AUTO_TEST_CASE( merkle_root )
{
  signed_block block;
  vector<signed_transaction> tx;
  vector<digest_type> t;
  const uint32_t num_tx = 10;

  for( uint32_t i=0; i<num_tx; i++ )
  {
    tx.emplace_back();
    tx.back().ref_block_prefix = i;
    t.push_back( tx.back().merkle_digest() );
  }

  auto c = []( const digest_type& digest ) -> checksum_type
  {   return checksum_type::hash( digest );   };

  auto d = []( const digest_type& left, const digest_type& right ) -> digest_type
  {   return digest_type::hash( std::make_pair( left, right ) );   };

  BOOST_CHECK( block.calculate_merkle_root() == checksum_type() );

  block.transactions.push_back( tx[0] );
  BOOST_CHECK( block.calculate_merkle_root() ==
    c(t[0])
    );

  digest_type dA, dB, dC, dD, dE, dI, dJ, dK, dM, dN, dO;

  /****************
    *              *
    *   A=d(0,1)   *
    *      / \     *
    *     0   1    *
    *              *
    ****************/

  dA = d(t[0], t[1]);

  block.transactions.push_back( tx[1] );
  BOOST_CHECK( block.calculate_merkle_root() == c(dA) );

  /*************************
    *                       *
    *         I=d(A,B)      *
    *        /        \     *
    *   A=d(0,1)      B=2   *
    *      / \        /     *
    *     0   1      2      *
    *                       *
    *************************/

  dB = t[2];
  dI = d(dA, dB);

  block.transactions.push_back( tx[2] );
  BOOST_CHECK( block.calculate_merkle_root() == c(dI) );

  /***************************
    *                         *
    *       I=d(A,B)          *
    *        /    \           *
    *   A=d(0,1)   B=d(2,3)   *
    *      / \    /   \       *
    *     0   1  2     3      *
    *                         *
    ***************************
    */

  dB = d(t[2], t[3]);
  dI = d(dA, dB);

  block.transactions.push_back( tx[3] );
  BOOST_CHECK( block.calculate_merkle_root() == c(dI) );

  /***************************************
    *                                     *
    *                  __M=d(I,J)__       *
    *                 /            \      *
    *         I=d(A,B)              J=C   *
    *        /        \            /      *
    *   A=d(0,1)   B=d(2,3)      C=4      *
    *      / \        / \        /        *
    *     0   1      2   3      4         *
    *                                     *
    ***************************************/

  dC = t[4];
  dJ = dC;
  dM = d(dI, dJ);

  block.transactions.push_back( tx[4] );
  BOOST_CHECK( block.calculate_merkle_root() == c(dM) );

  /**************************************
    *                                    *
    *                 __M=d(I,J)__       *
    *                /            \      *
    *        I=d(A,B)              J=C   *
    *       /        \            /      *
    *  A=d(0,1)   B=d(2,3)   C=d(4,5)    *
    *     / \        / \        / \      *
    *    0   1      2   3      4   5     *
    *                                    *
    **************************************/

  dC = d(t[4], t[5]);
  dJ = dC;
  dM = d(dI, dJ);

  block.transactions.push_back( tx[5] );
  BOOST_CHECK( block.calculate_merkle_root() == c(dM) );

  /***********************************************
    *                                             *
    *                  __M=d(I,J)__               *
    *                 /            \              *
    *         I=d(A,B)              J=d(C,D)      *
    *        /        \            /        \     *
    *   A=d(0,1)   B=d(2,3)   C=d(4,5)      D=6   *
    *      / \        / \        / \        /     *
    *     0   1      2   3      4   5      6      *
    *                                             *
    ***********************************************/

  dD = t[6];
  dJ = d(dC, dD);
  dM = d(dI, dJ);

  block.transactions.push_back( tx[6] );
  BOOST_CHECK( block.calculate_merkle_root() == c(dM) );

  /*************************************************
    *                                               *
    *                  __M=d(I,J)__                 *
    *                 /            \                *
    *         I=d(A,B)              J=d(C,D)        *
    *        /        \            /        \       *
    *   A=d(0,1)   B=d(2,3)   C=d(4,5)   D=d(6,7)   *
    *      / \        / \        / \        / \     *
    *     0   1      2   3      4   5      6   7    *
    *                                               *
    *************************************************/

  dD = d(t[6], t[7]);
  dJ = d(dC, dD);
  dM = d(dI, dJ);

  block.transactions.push_back( tx[7] );
  BOOST_CHECK( block.calculate_merkle_root() == c(dM) );

  /************************************************************************
    *                                                                      *
    *                             _____________O=d(M,N)______________      *
    *                            /                                   \     *
    *                  __M=d(I,J)__                                  N=K   *
    *                 /            \                              /        *
    *         I=d(A,B)              J=d(C,D)                 K=E           *
    *        /        \            /        \            /                 *
    *   A=d(0,1)   B=d(2,3)   C=d(4,5)   D=d(6,7)      E=8                 *
    *      / \        / \        / \        / \        /                   *
    *     0   1      2   3      4   5      6   7      8                    *
    *                                                                      *
    ************************************************************************/

  dE = t[8];
  dK = dE;
  dN = dK;
  dO = d(dM, dN);

  block.transactions.push_back( tx[8] );
  BOOST_CHECK( block.calculate_merkle_root() == c(dO) );

  /************************************************************************
    *                                                                      *
    *                             _____________O=d(M,N)______________      *
    *                            /                                   \     *
    *                  __M=d(I,J)__                                  N=K   *
    *                 /            \                              /        *
    *         I=d(A,B)              J=d(C,D)                 K=E           *
    *        /        \            /        \            /                 *
    *   A=d(0,1)   B=d(2,3)   C=d(4,5)   D=d(6,7)   E=d(8,9)               *
    *      / \        / \        / \        / \        / \                 *
    *     0   1      2   3      4   5      6   7      8   9                *
    *                                                                      *
    ************************************************************************/

  dE = d(t[8], t[9]);
  dK = dE;
  dN = dK;
  dO = d(dM, dN);

  block.transactions.push_back( tx[9] );
  BOOST_CHECK( block.calculate_merkle_root() == c(dO) );
}

BOOST_AUTO_TEST_CASE( adjust_balance_asset_test )
{
  ACTORS( (alice) );

  generate_block();

  BOOST_TEST_MESSAGE( "Testing adjust_balance for asset objects" );

  BOOST_TEST_MESSAGE( " --- Testing adding HIVE_SYMBOL" );
  db->adjust_balance( "alice", asset( 50000, HIVE_SYMBOL ) );
  BOOST_REQUIRE( db->get_balance( "alice", HIVE_SYMBOL ) == asset( 50000, HIVE_SYMBOL ) );

  BOOST_TEST_MESSAGE( " --- Testing deducting HIVE_SYMBOL" );
  HIVE_REQUIRE_THROW( db->adjust_balance( "alice", asset( -50001, HIVE_SYMBOL ) ), fc::assert_exception );
  db->adjust_balance( "alice", asset( -30000, HIVE_SYMBOL ) );
  db->adjust_balance( "alice", asset( -20000, HIVE_SYMBOL ) );
  BOOST_REQUIRE( db->get_balance( "alice", HIVE_SYMBOL ) == asset( 0, HIVE_SYMBOL ) );

  BOOST_TEST_MESSAGE( " --- Testing adding HBD_SYMBOL" );
  db->adjust_balance( "alice", asset( 100000, HBD_SYMBOL ) );
  BOOST_REQUIRE( db->get_balance( "alice", HBD_SYMBOL ) == asset( 100000, HBD_SYMBOL ) );

  BOOST_TEST_MESSAGE( " --- Testing deducting HBD_SYMBOL" );
  HIVE_REQUIRE_THROW( db->adjust_balance( "alice", asset( -100001, HBD_SYMBOL ) ), fc::assert_exception );
  db->adjust_balance( "alice", asset( -50000, HBD_SYMBOL ) );
  db->adjust_balance( "alice", asset( -25000, HBD_SYMBOL ) );
  db->adjust_balance( "alice", asset( -25000, HBD_SYMBOL ) );
  BOOST_REQUIRE( db->get_balance( "alice", HBD_SYMBOL ) == asset( 0, HBD_SYMBOL ) );

  auto initial_vesting = db->get_account( "alice" ).get_vesting();

  BOOST_TEST_MESSAGE( " --- Testing adding VEST_SYMBOL" );
  ilog( " --- Testing adding VEST_SYMBOL" );
  BOOST_REQUIRE_EQUAL( db->get_account( "alice" ).get_vesting(), initial_vesting );
  db->adjust_balance( "alice", asset( 100000, VESTS_SYMBOL ) );
  BOOST_REQUIRE_EQUAL( db->get_account( "alice" ).get_vesting(), initial_vesting + VEST_asset( 100000 ) );

  BOOST_TEST_MESSAGE( " --- Testing deducting VESTS_SYMBOL" );
  HIVE_REQUIRE_THROW( db->adjust_balance( "alice", asset( -1, VESTS_SYMBOL ) ), fc::assert_exception );
}

BOOST_AUTO_TEST_CASE( adjust_balance_tiny_asset_test )
{
   ACTORS( (alice) );

   generate_block();

   BOOST_TEST_MESSAGE( "Testing adjust_balance for tiny_asset objects" );

   BOOST_TEST_MESSAGE( " --- Testing adding HIVE_SYMBOL" );
   db->adjust_balance( "alice", HIVE_asset( 50000 ) );
   BOOST_REQUIRE( db->get_account( "alice" ).get_balance() == HIVE_asset( 50000 ) );

   BOOST_TEST_MESSAGE( " --- Testing deducting HIVE_SYMBOL" );
   HIVE_REQUIRE_THROW( db->adjust_balance( "alice", asset( -50001, HIVE_SYMBOL ) ), fc::assert_exception );
   db->adjust_balance( "alice", HIVE_asset( -30000 ) );
   db->adjust_balance( "alice", HIVE_asset( -20000 ) );
   BOOST_REQUIRE( db->get_account( "alice" ).get_balance() == HIVE_asset( 0 ) );

   BOOST_TEST_MESSAGE( " --- Testing adding HBD_SYMBOL" );
   db->adjust_balance( "alice", HBD_asset( 100000 ) );
   BOOST_REQUIRE( db->get_account( "alice" ).get_hbd_balance() == HBD_asset( 100000 ) );

   BOOST_TEST_MESSAGE( " --- Testing deducting HBD_SYMBOL" );
   HIVE_REQUIRE_THROW( db->adjust_balance( "alice", HBD_asset( -100001 ) ), fc::assert_exception );
   db->adjust_balance( "alice", HBD_asset( -50000 ) );
   db->adjust_balance( "alice", HBD_asset( -25000 ) );
   db->adjust_balance( "alice", HBD_asset( -25000 ) );
   BOOST_REQUIRE( db->get_account( "alice" ).get_hbd_balance() == HBD_asset( 0 ) );

   auto initial_vesting = db->get_account( "alice" ).get_vesting();

   BOOST_TEST_MESSAGE( " --- Testing adding VEST_SYMBOL" );
   BOOST_REQUIRE_EQUAL( db->get_account( "alice" ).get_vesting(), initial_vesting );
   db->adjust_balance( "alice", VEST_asset( 100000 ) );
   BOOST_REQUIRE_EQUAL( db->get_account( "alice" ).get_vesting(), initial_vesting + VEST_asset( 100000 ) );

   BOOST_TEST_MESSAGE( " --- Testing deducting VESTS_SYMBOL" );
   HIVE_REQUIRE_THROW( db->adjust_balance( "alice", VEST_asset( -1 ) ), fc::assert_exception );
}

BOOST_AUTO_TEST_CASE( tiny_asset_plus_op )
{
   share_type lhs_amount = 1000;
   share_type rhs_amount = 2000;
   share_type total_amount = lhs_amount + rhs_amount;
   HIVE_asset lhs = asset( lhs_amount, HIVE_SYMBOL );
   HIVE_asset rhs = asset( rhs_amount, HIVE_SYMBOL );
   HIVE_asset result = lhs + rhs;
   BOOST_REQUIRE(result.amount == total_amount);
}

BOOST_AUTO_TEST_CASE( tiny_asset_minus_op )
{
   share_type lhs_amount = 2500;
   share_type rhs_amount = 500;
   share_type total_amount = lhs_amount - rhs_amount;
   HIVE_asset lhs = asset( lhs_amount, HIVE_SYMBOL );
   HIVE_asset rhs = asset( rhs_amount, HIVE_SYMBOL );
   HIVE_asset result = lhs - rhs;
   BOOST_REQUIRE(result.amount == total_amount);
}

BOOST_AUTO_TEST_CASE( tiny_asset_plus_assign_op )
{
   share_type lhs_amount = 2500;
   share_type rhs_amount = 500;
   share_type total_amount = lhs_amount + rhs_amount;
   HIVE_asset lhs = asset( lhs_amount, HIVE_SYMBOL );
   HIVE_asset rhs = asset( rhs_amount, HIVE_SYMBOL );
   lhs += rhs;
   BOOST_REQUIRE(lhs.amount == total_amount);
}

BOOST_AUTO_TEST_CASE( tiny_asset_minus_assign_op )
{
   share_type lhs_amount = 2500;
   share_type rhs_amount = 500;
   share_type total_amount = lhs_amount - rhs_amount;
   HIVE_asset lhs = asset( lhs_amount, HIVE_SYMBOL );
   HIVE_asset rhs = asset( rhs_amount, HIVE_SYMBOL );
   lhs -= rhs;
   BOOST_REQUIRE(lhs.amount == total_amount);
}

BOOST_AUTO_TEST_CASE( tiny_asset_compare_ops )
{
   HIVE_asset bigger = asset(1000, HIVE_SYMBOL);
   HIVE_asset lower = asset(500, HIVE_SYMBOL);
   BOOST_CHECK_GT(bigger, lower);
   BOOST_CHECK_GE(bigger, lower);
   BOOST_CHECK_LE(lower, bigger);
   BOOST_CHECK_LT(lower, bigger);
   BOOST_CHECK(!(bigger < lower));
   BOOST_CHECK(!(bigger <= lower));
   BOOST_CHECK(!(lower >= bigger));
   BOOST_CHECK(!(lower > bigger));
}

BOOST_AUTO_TEST_CASE( tiny_asset_equality_op )
{
   HIVE_asset objA = asset(1000, HIVE_SYMBOL);
   HIVE_asset objB = asset(1000, HIVE_SYMBOL);
   HIVE_asset objX = asset(500, HIVE_SYMBOL);
   BOOST_CHECK_EQUAL(objA, objB);
   BOOST_CHECK_NE(objA, objX);
}

BOOST_AUTO_TEST_CASE( tiny_asset_mul_price )
{
   auto base = asset(1500, HIVE_SYMBOL);
   auto quote = asset(3000, HBD_SYMBOL);
   auto p = price(base, quote);
   auto hbds = HBD_asset(1000);
   auto hives = HIVE_asset(1000);
   BOOST_CHECK_EQUAL(hbds * p, asset(500, HIVE_SYMBOL));
   BOOST_CHECK_EQUAL(hives * p, asset(2000, HBD_SYMBOL));
}

uint8_t find_msb( const uint128_t& u )
{
  uint64_t x;
  uint8_t places;
  x      = (u.lo ? u.lo : 1);
  places = (u.hi ?   64 : 0);
  x      = (u.hi ? u.hi : x);
  return uint8_t( boost::multiprecision::detail::find_msb(x) + places );
}

uint64_t approx_sqrt( const uint128_t& x )
{
  if( (x.lo == 0) && (x.hi == 0) )
    return 0;

  uint8_t msb_x = find_msb(x);
  uint8_t msb_z = msb_x >> 1;

  uint128_t msb_x_bit = uint128_t(1) << msb_x;
  uint64_t  msb_z_bit = uint64_t (1) << msb_z;

  uint128_t mantissa_mask = msb_x_bit - 1;
  uint128_t mantissa_x = x & mantissa_mask;
  uint64_t mantissa_z_hi = (msb_x & 1) ? msb_z_bit : 0;
  uint64_t mantissa_z_lo = (mantissa_x >> (msb_x - msb_z)).lo;
  uint64_t mantissa_z = (mantissa_z_hi | mantissa_z_lo) >> 1;
  uint64_t result = msb_z_bit | mantissa_z;

  return result;
}

BOOST_AUTO_TEST_CASE( curation_weight_test )
{
  fc::uint128_t rshares = 856158;
  fc::uint128_t s = uint128_t( 0, 2000000000000ull );
  fc::uint128_t sqrt = approx_sqrt( rshares + 2 * s );
  uint64_t result = ( rshares / sqrt ).to_uint64();

  BOOST_REQUIRE( sqrt.to_uint64() == 2002250 );
  BOOST_REQUIRE( result == 0 );

  rshares = 0;
  sqrt = approx_sqrt( rshares + 2 * s );
  result = ( rshares / sqrt ).to_uint64();

  BOOST_REQUIRE( sqrt.to_uint64() == 2002250 );
  BOOST_REQUIRE( result == 0 );

  result = ( uint128_t( 0 ) - uint128_t( 0 ) ).to_uint64();

  BOOST_REQUIRE( result == 0 );
  rshares = uint128_t( 0, 3351842535167ull );

  for( int64_t i = 856158; i >= 0; --i )
  {
    uint64_t old_weight = util::evaluate_reward_curve( rshares - i, protocol::convergent_square_root, s ).to_uint64();
    uint64_t new_weight = util::evaluate_reward_curve( rshares, protocol::convergent_square_root, s ).to_uint64();

    BOOST_REQUIRE( old_weight <= new_weight );

    uint128_t w( new_weight - old_weight );

    w *= 300;
    w /= 300;
    BOOST_REQUIRE( w.to_uint64() == new_weight - old_weight );
  }

  //idump( (delta)(old_weight)(new_weight) );

}

#if !defined ENABLE_MIRA && !defined ENABLE_STD_ALLOCATOR
BOOST_AUTO_TEST_CASE( chain_object_size )
{
  //typical elements of various objects
  BOOST_CHECK_EQUAL( sizeof( account_object::id_type ), 4 ); //hidden first element of all objects (here just an example, all are the same size)
  BOOST_CHECK_EQUAL( sizeof( account_id_type ), 4 ); //all id_refs are of the same size
  BOOST_CHECK_EQUAL( sizeof( time_point_sec ), 4 );
  BOOST_CHECK_EQUAL( sizeof( share_type ), 8 );
  BOOST_CHECK_EQUAL( sizeof( HIVE_asset ), 8 ); //all tiny assets are of the same size
  BOOST_CHECK_EQUAL( sizeof( asset ), 16 );
  BOOST_CHECK_EQUAL( sizeof( account_name_type ), 16 );
  BOOST_CHECK_EQUAL( sizeof( shared_string ), 32 ); //it has dynamic component as well
  BOOST_CHECK_EQUAL( sizeof( price ), 32 );
  BOOST_CHECK_EQUAL( sizeof( t_vector< char > ), 32 ); //it has dynamic component as well, all vectors have the same static size

  /*
  The purpose of this test is to make you think about the impact on RAM when you make changes in chain objects.
  Also somewhat helps in catching new problems with alignment (f.e. when you added a flag member and object
  grew by 8 bytes it might be inevitable but it should prompt you to double check member placement).
  Finally, especially when you are adding new objects, you should think if there is a mechanism (resource cost or
  hard limit) that prevents use of the object creating operation in RAM attack.
  */

  //top RAM gluttons
  BOOST_CHECK_EQUAL( sizeof( comment_object ), 36 ); //85M+ growing fast
  BOOST_CHECK_EQUAL( sizeof( comment_content_object ), 104 ); //as many as comment_object, dynamic size matters the most, in HiveMind

  //permanent objects (no operation to remove)
  BOOST_CHECK_EQUAL( sizeof( account_object ), 488 ); //1.3M+
  BOOST_CHECK_EQUAL( sizeof( account_metadata_object ), 72 ); //as many as account_object, but only FatNode (also to be moved to HiveMind)
  BOOST_CHECK_EQUAL( sizeof( account_authority_object ), 248 ); //as many as account_object
  BOOST_CHECK_EQUAL( sizeof( liquidity_reward_balance_object ), 48 ); //obsolete - only created/modified up to HF12 (683 objects)
  BOOST_CHECK_EQUAL( sizeof( witness_object ), 352 ); //small but potentially as many as account_object

  //lasting objects (operation to create and remove, but with potential to grow)
  BOOST_CHECK_EQUAL( sizeof( vesting_delegation_object ), 56 ); //1M+ (potential of account_object squared !!!)
  BOOST_CHECK_EQUAL( sizeof( withdraw_vesting_route_object ), 48 ); //45k (potential of 10*account_object)
  BOOST_CHECK_EQUAL( sizeof( witness_vote_object ), 40 ); //450k (potential of 30*account_object)

  //buffered objects (operation to create, op/vop to remove after certain time)
  BOOST_CHECK_EQUAL( sizeof( transaction_object ), 64 ); //at most <1h> of transactions
  BOOST_CHECK_EQUAL( sizeof( vesting_delegation_expiration_object ), 40 ); //at most <5d> of undelegates
  BOOST_CHECK_EQUAL( sizeof( owner_authority_history_object ), 104 ); //at most <30d> of ownership updates
  BOOST_CHECK_EQUAL( sizeof( account_recovery_request_object ), 104 ); //at most <1d> of account recoveries
  BOOST_CHECK_EQUAL( sizeof( change_recovery_account_request_object ), 48 ); //at most <30d> of recovery account changes
  BOOST_CHECK_EQUAL( sizeof( comment_cashout_object ), 200 //at most <7d> of unpaid comments (all comments prior to HF19)
#ifdef HIVE_ENABLE_SMT
    + 32
#endif
  ); 
  BOOST_CHECK_EQUAL( sizeof( comment_vote_object ), 48 ); //at most <7d> of votes on unpaid comments
  BOOST_CHECK_EQUAL( sizeof( convert_request_object ), 56 ); //at most <3.5d> of conversion requests
  BOOST_CHECK_EQUAL( sizeof( escrow_object ), 104 ); //small but potentially lasting forever, limited to 255*account_object
  BOOST_CHECK_EQUAL( sizeof( savings_withdraw_object ), 104 ); //at most <3d> of saving withdrawals
  BOOST_CHECK_EQUAL( sizeof( limit_order_object ), 80 ); //at most <28d> of limit orders
  BOOST_CHECK_EQUAL( sizeof( decline_voting_rights_request_object ), 32 ); //at most <30d> of decline requests
  BOOST_CHECK_EQUAL( sizeof( proposal_object ), 144 ); //potentially infinite, but costs a lot to make (especially after HF24)
  BOOST_CHECK_EQUAL( sizeof( proposal_vote_object ), 32 ); //potentially infinite, but limited by account_object and time of proposal_object life

  //singletons (size only affects performance, especially with MIRA)
  BOOST_CHECK_EQUAL( sizeof( reward_fund_object ), 80 );
  BOOST_CHECK_EQUAL( sizeof( dynamic_global_property_object ), 344
#ifdef HIVE_ENABLE_SMT
    + 16
#endif
  );
  BOOST_CHECK_EQUAL( sizeof( block_summary_object ), 24 ); //always 64k objects
  BOOST_CHECK_EQUAL( sizeof( hardfork_property_object ), 88 );
  BOOST_CHECK_EQUAL( sizeof( feed_history_object ), 136 ); //dynamic size worth 7*24 of sizeof(price)
  BOOST_CHECK_EQUAL( sizeof( witness_schedule_object ), 536 );

  //TODO: categorize and evaluate size potential of SMT related objects:
  //account_regular_balance_object
  //account_rewards_balance_object
  //nai_pool_object
  //smt_token_object
  //smt_ico_object
  //smt_token_emissions_object
  //smt_contribution_object

  //only used in tests, but open for use in theory:
  //pending_optional_action_object
  //pending_required_action_object

  //not used in regular chain
  //operation_object //obsolete? AH plugin
  //account_history_object //obsolete? AH plugin
}
#endif

BOOST_AUTO_TEST_SUITE_END()
