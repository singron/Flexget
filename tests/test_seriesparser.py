from nose.tools import assert_raises
from nose.tools import raises
from flexget.utils.titles import SeriesParser, ParseWarning

#
# NOTE:
#
# Logging doesn't properly work if you run this test only as it is initialized
# in FlexGetBase which this does NOT use at all. I spent hour debugging why
# logging doesn't work ...
#

# try to get logging running ...
# enable enable_logging and add --nologcapture to nosetest to see debug
# (should not be needed, logging is not initialized properly?)

enable_logging = True

if enable_logging:
    level = 5
    import logging
    from flexget import initialize_logging
    initialize_logging(True)
    log = logging.getLogger()
    log.setLevel(level)
    # switch seriesparser logging to debug
    from flexget.utils.titles.series import log as parser_log
    parser_log.setLevel(level)


class TestSeriesParser(object):

    def parse(self, **kwargs):
        s = SeriesParser()
        s.name = kwargs['name']
        s.data = kwargs['data']
        s.parse()
        return s

    def test_proper(self):
        """SeriesParser: proper"""
        s = self.parse(name='Something Interesting', data='Something.Interesting.S01E02.Proper-FlexGet')
        assert s.season == 1
        assert s.episode == 2
        assert s.quality == 'unknown'
        assert s.proper_or_repack, 'did not detect proper from %s' % s.data
        s = self.parse(name='foobar', data='foobar 720p proper s01e01')
        assert s.proper_or_repack, 'did not detect proper from %s' % s.data

    def test_non_proper(self):
        """SeriesParser: non-proper"""
        s = self.parse(name='Something Interesting', data='Something.Interesting.S01E02-FlexGet')
        assert s.season == 1
        assert s.episode == 2
        assert s.quality == 'unknown'
        assert not s.proper_or_repack, 'detected proper'

    def test_basic(self):
        """SeriesParser: basic parsing"""
        s = self.parse(name='Something Interesting', data='The.Something.Interesting.S01E02-FlexGet')
        assert not s.valid, 'Should not be valid'

        s = self.parse(name='25', data='25.And.More.S01E02-FlexGet')
        assert s.valid, 'Fix the implementation, should not be valid'
        assert s.identifier == 'S01E02', 'identifier broken'

    @raises(Exception)
    def test_invalid_name(self):
        """SeriesParser: invalid name"""
        s = SeriesParser()
        s.name = 1
        s.data = 'Something'

    @raises(Exception)
    def test_invalid_data(self):
        """SeriesParser: invalid data"""
        s = SeriesParser()
        s.name = 'Something Interesting'
        s.data = 1

    def test_confusing(self):
        """SeriesParser: confusing (invalid) numbering scheme"""
        s = self.parse(name='Something', data='Something.2008x12.13-FlexGet')
        assert not s.episode, 'Should not have episode'
        assert not s.season, 'Should not have season'
        assert s.id == '2008-12-13', 'invalid id'
        assert s.valid, 'should not valid'

    def test_unwanted(self):
        """SeriesParser: unwanted hits (e.g. complete season)"""
        s = self.parse(name='Something', data='Something.1x0.Complete.Season-FlexGet')
        assert not s.valid, 'data %s should not be valid' % s.data

        s = self.parse(name='Something', data='Something.1xAll.Season.Complete-FlexGet')
        assert not s.valid, 'data %s should not be valid' % s.data

        s = self.parse(name='Something', data='Something Seasons 1 & 2 - Complete')
        assert not s.valid, 'data %s should not be valid' % s.data

        s = self.parse(name='Something', data='Something Seasons 4 Complete')
        assert not s.valid, 'data %s should not be valid' % s.data

        s = self.parse(name='Something', data='Something Seasons 1 2 3 4')
        assert not s.valid, 'data %s should not be valid' % s.data

        s = self.parse(name='Something', data='Something S6 E1-4')
        assert not s.valid, 'data %s should not be valid' % s.data

    def test_unwanted_disc(self):
        """SeriesParser: unwanted disc releases"""
        s = self.parse(name='Something', data='Something.S01D2.DVDR-FlexGet')
        assert not s.valid, 'data %s should not be valid' % s.data

    def test_season_x_ep(self):
        """SeriesParser: 01x02"""
        s = self.parse(name='Something', data='Something.01x02-FlexGet')
        assert (s.season == 1 and s.episode == 2), 'failed to parse 01x02'

        s = self.parse(name='Something', data='Something 1 x 2-FlexGet')
        assert (s.season == 1 and s.episode == 2), 'failed to parse 1 x 2'

        # Ticket #732
        s = self.parse(name='Something', data='Something - This is the Subtitle 14x9 [Group-Name]')
        assert (s.season == 14 and s.episode == 9), 'failed to parse %s' % s.data

    def test_ep_in_square_brackets(self):
        """SeriesParser: [S01] [E02] NOT IMPLEMENTED"""
        return

        # FIX: #402 .. a bit hard to do
        s = self.parse(name='Something', data='Something [S01] [E02]')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

    def test_ep_in_parenthesis(self):
        """SeriesParser: test ep in parenthesis"""
        s = self.parse(name='Something', data='Something (S01E02)')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

    def test_season_episode(self):
        """SeriesParser: season X, episode Y"""
        s = self.parse(name='Something', data='Something - Season 1, Episode 2')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

        s = self.parse(name='Something', data='Something - Season1, Episode2')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

        s = self.parse(name='Something', data='Something - Season1 Episode2')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

    def test_series_episode(self):
        """SeriesParser: series X, episode Y"""
        s = self.parse(name='Something', data='Something - Series 1, Episode 2')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

        s = self.parse(name='Something', data='Something - Series1, Episode2')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

        s = self.parse(name='Something', data='Something - Series1 Episode2')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

    def test_episode(self):
        """SeriesParser: episode X (assume season 1)"""
        s = self.parse(name='Something', data='Something - Episode2')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

        s = self.parse(name='Something', data='Something - Episode 2')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

        s = self.parse(name='Something', data='Something - Episode VIII')
        assert (s.season == 1 and s.episode == 8), 'failed to parse %s' % s

    def test_ep(self):
        """SeriesParser: ep X (assume season 1)"""
        s = self.parse(name='Something', data='Something - Ep2')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

        s = self.parse(name='Something', data='Something - Ep 2')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

        s = self.parse(name='Something', data='Something - Ep VIII')
        assert (s.season == 1 and s.episode == 8), 'failed to parse %s' % s

    def test_season_episode_of_total(self):
        """SeriesParser: season X YofZ"""
        s = self.parse(name='Something', data='Something Season 1 2of12')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

        s = self.parse(name='Something', data='Something Season 1, 2 of 12')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

    def test_episode_of_total(self):
        """SeriesParser: YofZ (assume season 1)"""
        s = self.parse(name='Something', data='Something 2of12')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

        s = self.parse(name='Something', data='Something 2 of 12')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s

    def test_digits(self):
        """SeriesParser: digits (UID)"""
        s = self.parse(name='Something', data='Something 01 FlexGet')
        assert (s.id == '01'), 'failed to parse %s' % s.data

        s = self.parse(name='Something', data='Something-121.H264.FlexGet')
        assert (s.id == '121'), 'failed to parse %s' % s.data

    def test_quality(self):
        """SeriesParser: quality"""
        s = self.parse(name='Foo Bar', data='Foo.Bar.S01E01.720p.HDTV.x264-FlexGet')
        assert (s.season == 1 and s.episode == 1), 'failed to parse episodes from %s' % s.data
        assert (s.quality == '720p'), 'failed to parse quality from %s' % s.data

        s = self.parse(name='Test', data='Test.S01E01.720p-FlexGet')
        assert s.quality == '720p', 'failed to parse quality from %s' % s.data

        s = self.parse(name='30 Suck', data='30 Suck 4x4 [HDTV - FlexGet]')
        assert s.quality == 'hdtv', 'failed to parse quality %s' % s.data

        s = self.parse(name='ShowB', data='ShowB.S04E19.Name of Ep.720p.WEB-DL.DD5.1.H.264')
        assert s.quality == 'web-dl', 'failed to parse quality %s' % s.data

    def test_quality_parenthesis(self):
        """SeriesParser: quality in parenthesis"""
        s = self.parse(name='Foo Bar', data='Foo.Bar.S01E01.[720p].HDTV.x264-FlexGet')
        assert (s.season == 1 and s.episode == 1), 'failed to parse episodes from %s' % s.data
        assert (s.quality == '720p'), 'failed to parse quality from %s' % s.data

        s = self.parse(name='Foo Bar', data='Foo.Bar.S01E01.(720p).HDTV.x264-FlexGet')
        assert (s.season == 1 and s.episode == 1), 'failed to parse episodes from %s' % s.data
        assert (s.quality == '720p'), 'failed to parse quality from %s' % s.data

        s = self.parse(name='Foo Bar', data='[720p]Foo.Bar.S01E01.HDTV.x264-FlexGet')
        assert (s.season == 1 and s.episode == 1), 'failed to parse episodes from %s' % s.data
        assert (s.quality == '720p'), 'failed to parse quality from %s' % s.data

    def test_numeric_names(self):
        """SeriesParser: numeric names (24)"""
        s = self.parse(name='24', data='24.1x2-FlexGet')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s.data

        s = self.parse(name='90120', data='90120.1x2-FlexGet')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s.data

    def test_group_prefix(self):
        """SeriesParser: [group] before name"""
        s = self.parse(name='Foo Bar', data='[l.u.l.z] Foo Bar - 11 (H.264) [5235532D].mkv')
        assert (s.id == '11'), 'failed to parse %s' % s.data

        s = self.parse(name='Foo Bar', data='[7.1.7.5] Foo Bar - 11 (H.264) [5235532D].mkv')
        assert (s.id == '11'), 'failed to parse %s' % s.data

    def test_hd_prefix(self):
        """SeriesParser: HD 720p before name"""
        s = self.parse(name='Foo Bar', data='HD 720p: Foo Bar - 11 (H.264) [5235532D].mkv')
        assert (s.id == '11'), 'failed to parse %s' % s.data
        assert (s.quality == '720p'), 'failed to pick up quality'

    def test_partially_numeric(self):
        """SeriesParser: partially numeric names"""
        s = self.parse(name='Foo 2009', data='Foo.2009.S02E04.HDTV.XviD-2HD[FlexGet]')
        assert (s.season == 2 and s.episode == 4), 'failed to parse %s' % s.data
        assert (s.quality == 'hdtv'), 'failed to parse quality from %s' % s.data

    def test_ignore_seasonpacks(self):
        """SeriesParser: ignoring season packs"""
        """
        s = SeriesParser()
        s.name = 'The Foo'
        s.expect_ep = False
        s.data = 'The.Foo.S04.1080p.FlexGet.5.1'
        assert_raises(ParseWarning, s.parse)
        """

        s = SeriesParser()
        s.name = 'Something'
        s.data = 'Something S02 Pack 720p WEB-DL-FlexGet'
        assert_raises(ParseWarning, s.parse)

        s = SeriesParser()
        s.name = 'The Foo'
        s.expect_ep = False
        s.data = 'The Foo S05 720p BluRay DTS x264-FlexGet'
        assert_raises(ParseWarning, s.parse)

        s = SeriesParser()
        s.name = 'The Foo'
        s.expect_ep = True
        s.data = 'The Foo S05 720p BluRay DTS x264-FlexGet'
        assert_raises(ParseWarning, s.parse)

    def _test_similar(self):
        pass
        """
        s = self.parse(name='Foo Bar', data='Foo.Bar:Doppelganger.S02E04.HDTV.FlexGet')
        assert not s.valid, 'should not have parser Foo.Bar:Doppelganger'
        s = self.parse(name='Foo Bar', data='Foo.Bar.Doppelganger.S02E04.HDTV.FlexGet')
        assert not s.valid, 'should not have parser Foo.Bar.Doppelganger'
        """

    def test_idiotic_numbering(self):
        """SeriesParser: idiotic 101, 102, 103, .. numbering"""
        s = SeriesParser()
        s.name = 'test'
        s.data = 'Test.706.720p-FlexGet'
        s.expect_ep = True
        s.parse()
        assert s.season == 7, 'didn''t pick up season'
        assert s.episode == 6, 'didn''t pick up episode'

    def test_idiotic_numbering_with_zero(self):
        """SeriesParser: idiotic 0101, 0102, 0103, .. numbering"""
        s = SeriesParser()
        s.name = 'test'
        s.data = 'Test.0706.720p-FlexGet'
        s.expect_ep = True
        s.parse()
        assert s.season == 7, 'season missing'
        assert s.episode == 6, 'episode missing'
        assert s.identifier == 'S07E06', 'identifier broken'

    def test_idiotic_invalid(self):
        """SeriesParser: idiotic confused by invalid"""
        s = SeriesParser()
        s.expect_ep = True
        s.name = 'test'
        s.data = 'Test.Revealed.WS.PDTV.XviD-aAF.5190458.TPB.torrent'
        assert_raises(ParseWarning, s.parse)
        assert not s.season == 5, 'confused, got season'
        assert not s.season == 4, 'confused, got season'
        assert not s.episode == 19, 'confused, got episode'
        assert not s.episode == 58, 'confused, got episode'

    def test_zeroes(self):
        """SeriesParser: test zeroes as a season, episode"""

        for data in ['Test.S00E00-FlexGet', 'Test.S00E01-FlexGet', 'Test.S01E00-FlexGet']:
            s = self.parse(name='Test', data=data)
            id = s.identifier
            assert s.valid, 'parser not a valid for %s' % data
            assert isinstance(id, basestring), 'id is not a string for %s' % data
            assert isinstance(s.season, int), 'season is not a int for %s' % data
            assert isinstance(s.episode, int), 'season is not a int for %s' % data

    def test_exact_name(self):
        """SeriesParser: test exact/strict name parsing"""

        s = SeriesParser()
        s.name = 'test'
        s.data = 'Test.Foobar.S01E02.720p-FlexGet'
        s.parse()
        assert s.valid, 'normal failed'

        s = SeriesParser()
        s.strict_name = True
        s.name = 'test'
        s.data = 'Test.A.S01E02.720p-FlexGet'
        s.parse()
        assert not s.valid, 'strict A failed'

        s = SeriesParser()
        s.strict_name = True
        s.name = 'Test AB'
        s.data = 'Test.AB.S01E02.720p-FlexGet'
        s.parse()
        assert s.valid, 'strict AB failed'

    def test_quality_as_ep(self):
        """SeriesParser: test that qualities are not picked as ep"""
        from flexget.utils import qualities
        for quality in qualities.registry.keys():
            s = SeriesParser()
            s.expect_ep = True
            s.name = 'FooBar'
            s.data = 'FooBar %s XviD-FlexGet' % quality
            assert_raises(ParseWarning, s.parse)

    def test_sound_as_ep(self):
        """SeriesParser: test that sound infos are not picked as ep"""
        for sound in SeriesParser.sounds:
            s = SeriesParser()
            s.name = 'FooBar'
            s.data = 'FooBar %s XViD-FlexGet' % sound
            assert_raises(ParseWarning, s.parse)

    def test_name_with_number(self):
        """SeriesParser: test number in a name"""
        s = SeriesParser()
        s.name = 'Storage 13'
        s.data = 'Storage 13 no ep number'
        assert_raises(ParseWarning, s.parse)

    def test_name_uncorrupted(self):
        """SeriesParser: test name doesn't get corrupted when cleaned"""
        s = self.parse(name='The New Adventures of Old Christine', data='The.New.Adventures.of.Old.Christine.S05E16.HDTV.XviD-FlexGet')
        assert s.name == 'The New Adventures of Old Christine'
        assert s.season == 5
        assert s.episode == 16
        assert s.quality == 'hdtv'

    def test_part(self):
        """SeriesParser: test parsing part numeral (assume season 1)"""
        s = self.parse(name='Test', data='Test.Pt.I.720p-FlexGet')
        assert (s.season == 1 and s.episode == 1), 'failed to parse %s' % s
        s = self.parse(name='Test', data='Test.Pt.VI.720p-FlexGet')
        assert (s.season == 1 and s.episode == 6), 'failed to parse %s' % s
        s = self.parse(name='Test', data='Test.Part.2.720p-FlexGet')
        assert (s.season == 1 and s.episode == 2), 'failed to parse %s' % s
        s = self.parse(name='Test', data='Test.Part3.720p-FlexGet')
        assert (s.season == 1 and s.episode == 3), 'failed to parse %s' % s

    def test_from_groups(self):
        """SeriesParser: test from groups"""
        s = SeriesParser()
        s.name = 'Test'
        s.data = 'Test.S01E01-Group'
        s.allow_groups = ['xxxx', 'group']
        s.parse()
        assert s.group == 'group', 'did not get group'

    def test_id_and_hash(self):
        """SeriesParser: Series with confusing hash"""
        s = self.parse(name='Something', data='Something 63 [560D3414]')
        assert (s.id == '63'), 'failed to parse %s' % s.data

        s = self.parse(name='Something', data='Something 62 [293A8395]')
        assert (s.id == '62'), 'failed to parse %s' % s.data

    def test_ticket_700(self):
        """SeriesParser: confusing name (#700)"""
        s = self.parse(name='Something', data='Something 9x02 - Episode 2')
        assert s.season == 9, 'failed to parse season'
        assert s.episode == 2, 'failed to parse episode'
