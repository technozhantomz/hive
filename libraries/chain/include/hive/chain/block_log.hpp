#pragma once
#include <fc/filesystem.hpp>
#include <hive/protocol/block.hpp>

extern "C"
{
  struct ZSTD_CCtx_s;
  typedef struct ZSTD_CCtx_s ZSTD_CCtx;
  struct ZSTD_DCtx_s;
  typedef struct ZSTD_DCtx_s ZSTD_DCtx;
}

namespace hive { namespace chain {

  using namespace hive::protocol;

  namespace detail { class block_log_impl; }

  /* The block log is an external append only log of the blocks. Blocks should only be written
    * to the log after they irreverisble as the log is append only. The log is a doubly linked
    * list of blocks. There is a secondary index file of only block positions that enables O(1)
    * random access lookup by block number.
    *
    * +---------+----------------+---------+----------------+-----+------------+-------------------+
    * | Block 1 | Pos of Block 1 | Block 2 | Pos of Block 2 | ... | Head Block | Pos of Head Block |
    * +---------+----------------+---------+----------------+-----+------------+-------------------+
    *
    * +----------------+----------------+-----+-------------------+
    * | Pos of Block 1 | Pos of Block 2 | ... | Pos of Head Block |
    * +----------------+----------------+-----+-------------------+
    *
    * The block log can be walked in order by deserializing a block, skipping 8 bytes, deserializing a
    * block, repeat... The head block of the file can be found by seeking to the position contained
    * in the last 8 bytes the file. The block log can be read backwards by jumping back 8 bytes, following
    * the position, reading the block, jumping back 8 bytes, etc.
    *
    * Blocks can be accessed at random via block number through the index file. Seek to 8 * (block_num - 1)
    * to find the position of the block in the main file.
    *
    * The main file is the only file that needs to persist. The index file can be reconstructed during a
    * linear scan of the main file.
    */

  class block_log {
    public:
      // in the block log (and index), the positions are stored as 64-bit integers.  We'll use the lower 
      // 48-bits as the actual position, and the upper 16 as flags that tell us how the block is stored
      // hi    lo|hi    lo|hi      |        |        |        |        |      lo|
      // c......d|<-dict->|<--------------------- position -------------------->|
      // c    = block_flags, one bit specifying the compression method, or uncompressed
      //        (this was briefly two bits when we were testing other compression methods)
      // d    = one bit, if 1 the block uses a custom compression dictionary
      // dict = the number specifying the dictionary used to compress the block, if d = 1, otherwise undefined
      // .    = unused
      enum class block_flags {
        uncompressed = 0,
        zstd = 1 
      };
      struct block_attributes_t {
        block_flags flags = block_flags::uncompressed;
        fc::optional<uint8_t> dictionary_number;
      };

      block_log();
      ~block_log();

      void open( const fc::path& file, bool read_only = false );

      void close();
      bool is_open()const;

      uint64_t append(const signed_block& b);
      uint64_t append_raw(const char* raw_block_data, size_t raw_block_size, block_attributes_t flags);

      void flush();
      std::tuple<std::unique_ptr<char[]>, size_t, block_attributes_t> read_raw_block_data_by_num(uint32_t block_num) const;
      static std::tuple<std::unique_ptr<char[]>, size_t> decompress_raw_block(std::tuple<std::unique_ptr<char[]>, size_t, block_attributes_t>&& raw_block_data_tuple);

      optional<signed_block> read_block_by_num( uint32_t block_num )const;
      optional<signed_block_header> read_block_header_by_num( uint32_t block_num )const;
      vector<signed_block> read_block_range_by_num( uint32_t first_block_num, uint32_t count )const;

      std::tuple<std::unique_ptr<char[]>, size_t, block_log::block_attributes_t> read_raw_head_block() const;
      signed_block read_head()const;
      const boost::shared_ptr<signed_block> head() const;
      void set_compression(bool enabled);
      void set_compression_level(int level);

      static std::tuple<std::unique_ptr<char[]>, size_t> compress_block_zstd(const char* uncompressed_block_data, size_t uncompressed_block_size, fc::optional<uint8_t> dictionary_number, 
                                                                             fc::optional<int> compression_level = fc::optional<int>(), 
                                                                             fc::optional<ZSTD_CCtx*> compression_context = fc::optional<ZSTD_CCtx*>());
      static std::tuple<std::unique_ptr<char[]>, size_t> decompress_block_zstd(const char* compressed_block_data, size_t compressed_block_size, 
                                                                               fc::optional<uint8_t> dictionary_number = fc::optional<int>(), 
                                                                               fc::optional<ZSTD_DCtx*> decompression_context_for_reuse = fc::optional<ZSTD_DCtx*>());
    private:
      void construct_index(bool resume = false);
      static std::tuple<std::unique_ptr<char[]>, size_t> decompress_raw_block(const char* raw_block_data, size_t raw_block_size, block_attributes_t attributes);

      std::unique_ptr<detail::block_log_impl> my;
  };

} }
FC_REFLECT_ENUM(hive::chain::block_log::block_flags, (uncompressed)(zstd))
FC_REFLECT(hive::chain::block_log::block_attributes_t, (flags)(dictionary_number))
